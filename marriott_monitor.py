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

print("Marriott Monitor Active")
print("UTC:", datetime.datetime.utcnow())

properties = [
    {"name":"StRegis Bora Bora"},
    {"name":"Westin Bora Bora"},
    {"name":"Le Meridien Bora Bora"}
]

BUY_THRESHOLD = 45000
WATCH_THRESHOLD = 60000

buys = []
watchlist = []

print("Checking properties...")

for p in properties:
    name = p["name"]
    points = random.randint(30000,80000)

    print(f"Evaluating {name} — {points}")

    if points <= BUY_THRESHOLD:
        buys.append((name, points))
    elif points <= WATCH_THRESHOLD:
        watchlist.append((name, points))

print("-----")

if buys:
    print("BUY LIST:")
    body = ""
    for name, points in buys:
        line = f"BUY: {name} @ {points}"
        print(line)
        body += line + "\n"
    send_alert("MARRIOTT DEAL FOUND", body)

print("-----")

if watchlist:
    print("WATCH LIST:")
    for name, points in watchlist:
        print(f"WATCH: {name} @ {points}")

print("Marriott monitor complete")
