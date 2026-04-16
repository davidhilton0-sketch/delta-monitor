import json
import os
import smtplib
import time
import datetime
import urllib.request
import urllib.error
import urllib.parse
from email.mime.text import MIMEText

ORIGIN_AIRPORTS = ["ATL", "LAX", "SEA", "SLC"]
DESTINATION = "PPT"
GOOD_THRESHOLD = 120000
WATCH_THRESHOLD = 150000

SEATS_AERO_API_KEY = os.environ.get("SEATS_AERO_API_KEY", "").strip()
GMAIL_USER = os.environ.get("GMAIL_USER", "").strip()
GMAIL_PASS = os.environ.get("GMAIL_PASS", "").strip()
EMAIL_TO = "4042293044@tmomail.net"

print("Delta Monitor Active")
print("UTC:", datetime.datetime.utcnow())

if not SEATS_AERO_API_KEY:
    print("[FATAL] SEATS_AERO_API_KEY is not set.")
    raise SystemExit(1)

print(f"[CONFIG] Key length: {len(SEATS_AERO_API_KEY)} First 4: {SEATS_AERO_API_KEY[:4]}")

start_date = datetime.date.today().isoformat()
end_date = (datetime.date.today() + datetime.timedelta(days=90)).isoformat()

alerts = []
watchlist = []

print("Checking routes...")

for origin in ORIGIN_AIRPORTS:
    route_name = f"{origin}-PPT"

    params = urllib.parse.urlencode({
        "origin_airport": origin,
        "destination_airport": DESTINATION,
        "start_date": start_date,
        "end_date": end_date,
        "cabins": "business",
        "sources": "delta",
        "take": 10,
        "order_by": "lowest_mileage"
    })

    url = f"https://seats.aero/partnerapi/search?{params}"
    print(f"[API] GET {url}")

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {SEATS_AERO_API_KEY}")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read().decode("utf-8")
            print(f"[API] Status: {response.status} Bytes: {len(raw)}")
            data = json.loads(raw)
            records = data.get("data", [])
            print(f"[API] Records for {origin}: {len(records)}")

            for record in records:
                if not record.get("JAvailable", False):
                    continue
                miles = int(record.get("JMileageCost", 0))
                if miles <= 0:
                    continue
                if miles <= GOOD_THRESHOLD:
                    alerts.append((route_name, miles))
                elif miles <= WATCH_THRESHOLD:
                    watchlist.append((route_name, miles))

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        print(f"[ERROR] HTTP {e.code} for {origin}: {e.reason}")
        print(f"[ERROR] Body: {body}")
        if e.code in (401, 403):
            raise SystemExit(1)

    except urllib.error.URLError as e:
        print(f"[ERROR] Network error for {origin}: {e.reason}")

    except Exception as e:
        print(f"[ERROR] Unexpected error for {origin}: {e}")

    time.sleep(2)

print("-----")

if alerts:
    print("GOOD DEALS:")
    for route, miles in alerts:
        print(f"BUY: {route} @ {miles:,}")
else:
    print("No good deals")

print("-----")

if watchlist:
    print("WATCH LIST:")
    for route, miles in watchlist:
        print(f"WATCH: {route} @ {miles:,}")
else:
    print("No watch routes")

if alerts and GMAIL_USER and GMAIL_PASS:
    body = "DELTA BUSINESS DEALS\n\n"
    for route, miles in alerts:
        body += f"BUY: {route} @ {miles:,} miles\n"
    body += f"\nChecked: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"

    try:
        msg = MIMEText(body)
        msg["Subject"] = f"DELTA DEAL: {alerts[0][0]} {alerts[0][1]:,} miles"
        msg["From"] = GMAIL_USER
        msg["To"] = EMAIL_TO
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, EMAIL_TO, msg.as_string())
        print("[SENT] Alert email sent")
    except Exception as e:
        print(f"[ERROR] Email failed: {e}")

print("Monitor complete")
