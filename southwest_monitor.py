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

print("Southwest Monitor Active")
print("UTC:", datetime.datetime.utcnow())

routes = [
    {"origin":"ATL","dest":"DEN"},
    {"origin":"ATL","dest":"LAS"},
    {"origin":"ATL","dest":"PHX"}
]

GOOD_THRESHOLD = 8000
WATCH_THRESHOLD = 12000

alerts = []
watchlist = []

print("Checking routes...")

for r in routes:
    route_name = f"{r['origin']}-{r['dest']}"
    points = random.randint(6000,15000)

    print(f"Evaluating {route_name} — {points}")

    if points <= GOOD_THRESHOLD:
        alerts.append((route_name, points))
    elif points <= WATCH_THRESHOLD:
        watchlist.append((route_name, points))

print("-----")

if alerts:
    print("GOOD DEALS:")
    body = ""
    for route, points in alerts:
        line = f"BUY: {route} @ {points}"
        print(line)
        body += line + "\n"
    send_alert("SOUTHWEST DEAL FOUND", body)

print("-----")

if watchlist:
    print("WATCH LIST:")
    for route, points in watchlist:
        print(f"WATCH: {route} @ {points}")

print("Southwest monitor complete")
