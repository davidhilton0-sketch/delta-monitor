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
CABIN = "business"
THRESHOLD_MILES = 150000
SEARCH_DAYS_AHEAD = 90

SEATS_AERO_BASE = "https://seats.aero/api/availability"

SEATS_AERO_API_KEY = os.environ.get("SEATS_AERO_API_KEY", "")
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_PASS = os.environ.get("GMAIL_PASS", "")
EMAIL_TO = "4042293044@tmomail.net"

def send_alert(subject, body):
    if not GMAIL_USER or not GMAIL_PASS:
        print("[SKIP] Email not configured")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_PASS)
        smtp.sendmail(GMAIL_USER, EMAIL_TO, msg.as_string())

def fetch_availability(origin):
    start_date = datetime.date.today().isoformat()
    end_date = (datetime.date.today() + datetime.timedelta(days=SEARCH_DAYS_AHEAD)).isoformat()

    params = urllib.parse.urlencode({
        "origin_airport": origin,
        "destination_airport": DESTINATION,
        "cabin": CABIN,
        "start_date": start_date,
        "end_date": end_date,
        "take": 10
    })

    url = f"{SEATS_AERO_BASE}?{params}"
    print(f"[API] GET {url}")

    req = urllib.request.Request(
        url,
        headers={
            "Partner-Authorization": SEATS_AERO_API_KEY,
            "Accept": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            data = json.loads(response.read().decode("utf-8"))

            print(f"[API] Status: {status}")
            print(f"[API] Records: {len(data.get('data', []))}")

            return data.get("data", [])

    except urllib.error.HTTPError as e:
        print(f"[ERROR] HTTP {e.code}")
        if e.code == 401:
            print("[FATAL] API KEY INVALID")
        return []

def main():
    print("[START] Delta Monitor")
    print("UTC:", datetime.datetime.utcnow())

    if not SEATS_AERO_API_KEY:
        print("[FATAL] Missing SEATS_AERO_API_KEY")
        return

    for origin in ORIGIN_AIRPORTS:
        print(f"\nChecking {origin} → {DESTINATION}")

        records = fetch_availability(origin)

        for r in records:
            miles = r.get("JMileageCost", 0)

            if miles and miles < THRESHOLD_MILES:
                msg = f"{origin}-{DESTINATION} {miles} miles"
                print("[DEAL]", msg)
                send_alert("Delta Deal Found", msg)

        time.sleep(3)

    print("\n[DONE]")

if __name__ == "__main__":
    main()
