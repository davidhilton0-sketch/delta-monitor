import datetime
import random

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
    for route, points in alerts:
        print(f"BUY: {route} @ {points}")
else:
    print("No good deals")

print("-----")

if watchlist:
    print("WATCH LIST:")
    for route, points in watchlist:
        print(f"WATCH: {route} @ {points}")
else:
    print("No watch routes")

print("Southwest monitor complete")
