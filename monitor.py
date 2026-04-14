import datetime

print("Delta Monitor Active")
print("UTC:", datetime.datetime.utcnow())

# Placeholder logic — proves decision engine runs
routes = [
    "ATL-LAX-PPT",
    "ATL-SEA-PPT",
    "ATL-SLC-PPT"
]

threshold = 150000

print("Checking routes...")

for route in routes:
    print(f"Evaluating {route}...")

print("No deals found")
