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
CABINS = "business"
SOURCES = "delta"
SEARCH_DAYS_AHEAD = 90

SEATS_AERO_BASE = "https://seats.aero/partnerapi/search"

SEATS_AERO_API_KEY = os.environ.get("SEATS_AERO_API_KEY", "").strip()
GMAIL_USER = os.environ.get("GMAIL_USER", "").strip()
GMAIL_PASS = os.environ.get("GMAIL_PASS", "").strip()
EMAIL_TO = "4042293044@tmomail.net"

def fetch_availability(origin):
    start_date = datetime.date.today().isoformat()
    end_date = (datetime.date.today() + datetime.timedelta(days=SEARCH_DAYS_AHEAD)).isoformat()

    params = urllib.parse.urlencode({
        "origin_airport": origin,
        "destination_airport": DESTINATION,
        "start_date": start_date,
        "end_date": end_date,
        "cabins": CABINS,
        "sources": SOURCES,
        "take": 100,
        "order_by": "lowest_mileage"
    })

    url = f"{SEATS_AERO_BASE}?{params}"
    print(f"[API] GET {url}")

    req = urllib.request.Request(url)
    req.add_header("Partner-Authorization", SEATS_AERO_API_KEY)
    req.add_header("Accept", "application/json")

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print(f"[API] Status: {resp.status}")
        print(f"[API] Records: {len(data.get('data', []))}")

def main():
    print(f"[START] {datetime.datetime.utcnow()}")
    for origin in ORIGIN_AIRPORTS:
        print(f"[ROUTE] {origin} → {DESTINATION}")
        fetch_availability(origin)

if __name__ == "__main__":
    main()
