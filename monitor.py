import datetime

print("Delta Monitor Active")
print("UTC:", datetime.datetime.utcnow())

routes = [
    ("ATL-LAX-PPT", 165000),
    ("ATL-SEA-PPT", 142000),
    ("ATL-SLC-PPT", 98000)
]

GOOD_THRESHOLD = 120000
WATCH_THRESHOLD = 150000

print("Checking routes...")

for route, price in routes:
    print(f"Evaluating {route} — {price}")

    if price <= GOOD_THRESHOLD:
        print("GOOD DEAL")
    elif price <= WATCH_THRESHOLD:
        print("WATCH")
    else:
        print("IGNORE")

print("Decision engine complete")
