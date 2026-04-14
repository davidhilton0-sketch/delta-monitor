import datetime

print("Delta Monitor Active")
print("UTC:", datetime.datetime.utcnow())

routes = [
    ("ATL", "LAX", "PPT", 165000),
    ("ATL", "SEA", "PPT", 142000),
    ("ATL", "SLC", "PPT", 98000)
]

GOOD_THRESHOLD = 120000
WATCH_THRESHOLD = 150000

print("Checking routes...")

for origin, gateway, dest, price in routes:
    route_name = f"{origin}-{gateway}-{dest}"
    print(f"Evaluating {route_name} — {price}")

    if price <= GOOD_THRESHOLD:
        print("GOOD DEAL:", route_name)
    elif price <= WATCH_THRESHOLD:
        print("WATCH:", route_name)
    else:
        print("IGNORE:", route_name)

print("Route model complete")
