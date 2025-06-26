from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import os
import json
from faker import Faker
import uuid
from random import choice, randint, uniform
import random

fake = Faker()
num_rows = 100  # adjust as needed

print("Simulating supplier logs...")

category_part_map = {
    "parts": ["engine valve", "landing gear", "hydraulic pump"],
    "meals": ["veg meal", "non-veg meal", "snack box"],
    "tech": ["radar module", "nav sensor", "wifi router"]
}

supplier_list = [
    {"supplier_id": "SUP-001", "supplier": "AeroParts Inc."},
    {"supplier_id": "SUP-002", "supplier": "SkyMeals Co."},
    {"supplier_id": "SUP-003", "supplier": "FlightTech Solutions"}
]

# Load flight IDs from JSON file
json_path = os.path.join("data", "keys", "flight_ids.json")
with open(json_path, "r") as f:
    flight_ids = json.load(f)

supplier_map = {}
data = []

for flight_id in flight_ids:
    for _ in range(randint(2, 3)):  # 2–3 orders per flight
        supplier = random.choice(supplier_list)
        category = random.choice(list(category_part_map.keys()))
        part = random.choice(category_part_map[category])
        status = choice(["on-time", "delayed", "lost", "backordered"])
        delay_days = randint(1, 10) if status in ["delayed", "backordered"] else 0

        row = {
            "order_id": "ORD-" + str(uuid.uuid4())[:8],
            "supplier_id": supplier["supplier_id"],
            "supplier": supplier["supplier"],
            "category": category,
            "part": part,
            "order_date": fake.date_between(start_date='-30d', end_date='today'),
            "expected_delivery": fake.date_between(start_date='today', end_date='+15d'),
            "status": status,
            "delay_days": delay_days,
            "cost_usd": round(uniform(500, 20000), 2),
            "flight_id": flight_id,
            "flight_day": fake.date_between(start_date='today', end_date='+30d'),
            "recorded_at": datetime.utcnow().isoformat()
        }
        data.append(row)

df = pd.DataFrame(data)
print(df.head())

# Save to file
today = datetime.utcnow().strftime("%Y-%m-%d")
output_path = Path(f"data/raw/suppliers/supplier_logs_{today}.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_path, index=False)
print(f"Supplier logs saved to {output_path}")
