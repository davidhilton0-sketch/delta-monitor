import datetime

print("Delta Monitor Active")
print("UTC:", datetime.datetime.utcnow())

routes = [
    {"origin":"ATL","gateway":"LAX","dest":"PPT","price":165000},
    {"origin":"ATL","gateway":"SEA","dest":"PPT","price":142000},
    {"origin":"ATL","gateway":"SLC","dest":"PPT","price":98000}
]

GOOD_THRESHOLD = 120000
WATCH_THRESHOLD = 150000

alerts = []
watchlist = []

print("Checking routes...")

for r in routes:
    route_name = f"{r['origin']}-{r['gateway']}-{r['dest']}"
    price = r["price"]

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
