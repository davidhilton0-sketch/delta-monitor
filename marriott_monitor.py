import datetime
import random

print("Marriott Monitor Active")
print("UTC:", datetime.datetime.utcnow())

properties = [
    {"name":"StRegis Bora Bora","points":random.randint(35000,90000)},
    {"name":"Westin Bora Bora","points":random.randint(30000,80000)},
    {"name":"Le Meridien Bora Bora","points":random.randint(25000,70000)}
]

BUY_THRESHOLD = 45000
WATCH_THRESHOLD = 60000

buys = []
watchlist = []

print("Checking properties...")

for p in properties:
    name = p["name"]
    points = p["points"]

    print(f"Evaluating {name} — {points}")

    if points <= BUY_THRESHOLD:
        buys.append((name, points))
    elif points <= WATCH_THRESHOLD:
        watchlist.append((name, points))

print("-----")

if buys:
    print("BUY LIST:")
    for name, points in buys:
        print(f"BUY: {name} @ {points}")
else:
    print("No buy properties")

print("-----")

if watchlist:
    print("WATCH LIST:")
    for name, points in watchlist:
        print(f"WATCH: {name} @ {points}")
else:
    print("No watch properties")

print("Marriott monitor complete")
