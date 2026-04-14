import datetime
import random
import smtplib
import os
from email.message import EmailMessage

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_PASS"]
EMAIL_TO = "4042293044@tmomail.net"

def send_alert(subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = EMAIL_TO
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_PASS)
        smtp.send_message(msg)

print("Delta Monitor Active")
print("UTC:", datetime.datetime.utcnow())

routes = [
    {"origin":"ATL","gateway":"LAX","dest":"PPT"},
    {"origin":"ATL","gateway":"SEA","dest":"PPT"},
    {"origin":"ATL","gateway":"SLC","dest":"PPT"}
]

GOOD_THRESHOLD = 120000
WATCH_THRESHOLD = 150000

alerts = []
watchlist = []

print("Checking routes...")

for r in routes:
    route_name = f"{r['origin']}-{r['gateway']}-{r['dest']}"
    price = random.randint(90000, 170000)

    print(f"Evaluating {route_name} — {price}")

    if price <= GOOD_THRESHOLD:
        alerts.append((route_name, price))
    elif price <= WATCH_THRESHOLD:
        watchlist.append((route_name, price))

print("-----")

if alerts:
    print("GOOD DEALS:")
    body = ""
    for route, price in alerts:
        line = f"BUY: {route} @ {price}"
        print(line)
        body += line + "\n"
    send_alert("DELTA DEAL FOUND", body)

print("-----")

if watchlist:
    print("WATCH LIST:")
    for route, price in watchlist:
        print(f"WATCH: {route} @ {price}")

print("Monitor complete")
