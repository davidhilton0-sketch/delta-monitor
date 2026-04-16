import json
import os
import smtplib
import time
import datetime
import urllib.request
import urllib.error
import urllib.parse
from email.mime.text import MIMEText

# ============================================================
# CONFIGURATION
# ============================================================
ORIGIN_AIRPORTS = ["ATL", "LAX", "SEA", "SLC"]
DESTINATION = "PPT"
CABIN = "business"
THRESHOLD_MILES = 150000
SEARCH_DAYS_AHEAD = 90
SUPPRESS_HOURS = 6
PERSISTENCE_FILE = "delta_alerts.json"
REQUEST_SLEEP_SECONDS = 4
SEATS_AERO_BASE = "https://seats.aero/api/availability"

SEATS_AERO_API_KEY = os.environ.get("SEATS_AERO_API_KEY", "").strip()
GMAIL_USER = os.environ.get("GMAIL_USER", "").strip()
GMAIL_PASS = os.environ.get("GMAIL_PASS", "").strip()
EMAIL_TO = "4042293044@tmomail.net"

# ============================================================
# STARTUP VALIDATION
# ============================================================
def validate():
    if not SEATS_AERO_API_KEY:
        print("[FATAL] SEATS_AERO_API_KEY is empty or not set.")
        raise SystemExit(1)
    if "\n" in SEATS_AERO_API_KEY or "\r" in SEATS_AERO_API_KEY:
        print("[FATAL] SEATS_AERO_API_KEY contains illegal whitespace characters. Re-save the secret without newlines.")
        raise SystemExit(1)
    print(f"[CONFIG] API key loaded. Length: {len(SEATS_AERO_API_KEY)} chars. First 4: {SEATS_AERO_API_KEY[:4]}...")
    print(f"[CONFIG] Gmail user: {GMAIL_USER or 'NOT SET'}")

# ============================================================
# DEAL TIER
# ============================================================
def tier_label(miles):
    if miles <= 80000:
        return "RARE"
    if miles <= 100000:
        return "STRONG"
    if miles <= 120000:
        return "VERY GOOD"
    if miles <= 150000:
        return "GOOD"
    return None

# ============================================================
# PERSISTENCE
# ============================================================
def load_sent_alerts():
    if not os.path.exists(PERSISTENCE_FILE):
        return {}
    try:
        with open(PERSISTENCE_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Could not load persistence file: {e}")
        return {}

def save_sent_alerts(alerts):
    try:
        with open(PERSISTENCE_FILE, "w") as f:
            json.dump(alerts, f, indent=2)
    except Exception as e:
        print(f"[WARN] Could not save persistence file: {e}")

def is_suppressed(key, sent_alerts):
    if key not in sent_alerts:
        return False
    try:
        last_sent = datetime.datetime.fromisoformat(sent_alerts[key])
        elapsed = (datetime.datetime.utcnow() - last_sent).total_seconds()
        return elapsed < SUPPRESS_HOURS * 3600
    except Exception:
        return False

def mark_sent(key, sent_alerts):
    sent_alerts[key] = datetime.datetime.utcnow().isoformat()

# ============================================================
# FETCH
# ============================================================
def fetch_availability(origin):
    start_date = datetime.date.today().isoformat()
    end_date = (datetime.date.today() + datetime.timedelta(days=SEARCH_DAYS_AHEAD)).isoformat()

    params = urllib.parse.urlencode({
        "origin_airport": origin,
        "destination_airport": DESTINATION,
        "cabin": CABIN,
        "start_date": start_date,
        "end_date": end_date,
        "take": 100,
        "order_by": "lowest_mileage"
    })

    url = f"{SEATS_AERO_BASE}?{params}"
    print(f"[API] Requesting: {url}")

    req = urllib.request.Request(url)
    req.add_header("Partner-Authorization", SEATS_AERO_API_KEY)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "delta-monitor/1.0")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            raw = resp.read().decode("utf-8")
            print(f"[API] Status: {status} | Bytes: {len(raw)}")
            data = json.loads(raw)
            records = data.get("data", [])
            print(f"[API] Records for {origin}: {len(records)}")
            return records

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:400]
        print(f"[ERROR] HTTP {e.code} for {origin}: {e.reason}")
        print(f"[ERROR] Response body: {body}")
        if e.code == 401:
            print("[FATAL] 401 — API key rejected. Verify key in GitHub secrets and re-save without trailing whitespace.")
            raise SystemExit(1)
        return []

    except urllib.error.URLError as e:
        print(f"[ERROR] Network error for {origin}: {e.reason}")
        return []

    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parse failure for {origin}: {e}")
        return []

# ============================================================
# FILTER
# ============================================================
def extract_deals(records, origin):
    deals = []
    for record in records:
        try:
            if not record.get("JAvailable", False):
                continue
            mileage = int(record.get("JMileageCost", 0))
            if mileage <= 0:
                continue
            tier = tier_label(mileage)
            if tier is None:
                continue
            deals.append({
                "origin": origin,
                "destination": DESTINATION,
                "mileage": mileage,
                "tier": tier,
                "carrier": record.get("Carriers", "Unknown"),
                "date": record.get("ParsedDate", record.get("Date", "Unknown")),
                "seats": record.get("JRemainingSeats", "?"),
                "source": record.get("Source", "Unknown"),
            })
        except Exception as e:
            print(f"[WARN] Skipping record: {e}")
    deals.sort(key=lambda x: x["mileage"])
    return deals

# ============================================================
# ALERTS
# ============================================================
def format_email(deal):
    return (
        f"DELTA BUSINESS DEAL\n"
        f"{deal['origin']}–{deal['destination']}\n"
        f"{deal['mileage']:,} miles round trip\n"
        f"Tier: {deal['tier']}\n"
        f"Carrier: {deal['carrier']}\n"
        f"Cabin: Business\n"
        f"Date: {deal['date']}\n"
        f"Seats: {deal['seats']}\n"
        f"Program: {deal['source']}\n"
        f"Checked: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
    )

def format_sms(deal):
    return (
        f"DELTA {deal['tier']}\n"
        f"{deal['origin']}-{deal['destination']}\n"
        f"{deal['mileage']:,}mi {deal['carrier']}\n"
        f"{deal['date']}"
    )

def alert_key(deal):
    return f"delta-{deal['origin']}-{deal['destination']}-{deal['mileage']}-{deal['date']}"

def send_email(subject, body, to_address):
    if not GMAIL_USER or not GMAIL_PASS or not to_address:
        print(f"[SKIP] Email not configured. Subject: {subject}")
        return False
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = GMAIL_USER
        msg["To"] = to_address
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, to_address, msg.as_string())
        print(f"[SENT] {to_address}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("[ERROR] Gmail auth failed. Check GMAIL_USER and GMAIL_PASS secrets.")
        return False
    except Exception as e:
        print(f"[ERROR] Email failed: {e}")
        return False

def dispatch(deal, sent_alerts):
    key = alert_key(deal)
    if is_suppressed(key, sent_alerts):
        print(f"[SKIP] Suppressed: {key}")
        return False
    subject = f"DELTA {deal['tier']}: {deal['origin']}–{deal['destination']} {deal['mileage']:,}mi Business"
    sent = send_email(subject, format_email(deal), EMAIL_TO)
    if GMAIL_USER:
        send_email(subject, format_sms(deal), EMAIL_TO)
    if sent:
        mark_sent(key, sent_alerts)
    return sent

# ============================================================
# MAIN
# ============================================================
def main():
    print(f"[START] {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    validate()

    sent_alerts = load_sent_alerts()
    total_records = 0
    total_deals = 0
    total_sent = 0

    for i, origin in enumerate(ORIGIN_AIRPORTS):
        print(f"\n[ROUTE] {origin} → {DESTINATION}")
        records = fetch_availability(origin)
        total_records += len(records)
        deals = extract_deals(records, origin)
        total_deals += len(deals)

        for deal in deals:
            print(f"  [{deal['tier']}] {deal['mileage']:,} mi | {deal['carrier']} | {deal['date']}")
            if dispatch(deal, sent_alerts):
                total_sent += 1

        if i < len(ORIGIN_AIRPORTS) - 1:
            time.sleep(REQUEST_SLEEP_SECONDS)

    save_sent_alerts(sent_alerts)
    print(f"\n[DONE] Records={total_records} Deals={total_deals} Sent={total_sent}")

if __name__ == "__main__":
    main()
