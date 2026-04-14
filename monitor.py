import datetime
import random

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
    for route, price in alerts:
        print(f"BUY: {route} @ {price}")
else:
    print("No good deals")

print("-----")

if watchlist:
    print("WATCH LIST:")
    for route, price in watchlist:
        print(f"WATCH: {route} @ {price}")
else:
    print("No watch routes")

print("Monitor complete")
