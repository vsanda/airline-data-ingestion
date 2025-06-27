import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
import pandas as pd
import os
import json
from faker import Faker
import uuid
from random import choice, randint, uniform
from data.static.dim_suppliers import dim_suppliers
from data.static.dim_flights import dim_flights
from data.static.dim_aircraft import dim_aircraft
from utils.save_utils import save_csv
import random

fake = Faker()

print("Simulating supplier logs...")

# Load flight IDs from JSON file
json_path = os.path.join("data", "keys", "flight_ids.json")
with open(json_path, "r") as f:
    flight_ids = json.load(f)

dim_flights_df = pd.DataFrame(dim_flights)
dim_aircraft_df = pd.DataFrame(dim_aircraft)
merged_df = dim_flights_df.merge(dim_aircraft_df, on='aircraft_id', how='left')

def generate_and_save_supply_orders():
    data = []

    for i, row in merged_df.iterrows():
        flight_id = row["flight_id"]
        aircraft_id = row["aircraft_id"]
        capacity = row["max_capacity"]
        flight_day = row["flight_day"]  # default fallback

        for supplier in dim_suppliers:
            service_type = supplier["service_type"]

            include = (
                service_type == "Fuel" or
                (service_type == "Maintenance" and random.random() < 0.3) or
                (service_type == "Catering" and random.random() < 0.5)
            )

            if include:
                status = random.choices(["on-time", "delayed"], weights=[85, 15])[0]

                if service_type == "Fuel":
                    cost_usd = None  # Leave blank for silver calc
                elif service_type == "Maintenance":
                    base_cost = 2000
                    multiplier = 1.5 if capacity > 200 else 1.0
                    cost_usd = round(base_cost * multiplier * uniform(0.9, 1.2), 2)
                elif service_type == "Catering":
                    per_passenger = uniform(15, 30)
                    cost_usd = round(per_passenger * capacity * uniform(0.9, 1.1), 2)

                row = {
                    "order_id": "ORD-" + str(uuid.uuid4())[:8],
                    "supplier_id": supplier["supplier_id"],
                    "supplier": supplier["name"],
                    "service_type": service_type,
                    "flight_id": flight_id,
                    "aircraft_id": aircraft_id,
                    "order_date": fake.date_between(start_date='-30d', end_date='today').isoformat(),
                    "expected_delivery": fake.date_between(start_date='today', end_date='+15d').isoformat(),
                    "status": status,
                    "cost_usd": cost_usd,
                    "flight_day": flight_day,
                    "recorded_at": datetime.utcnow().isoformat()
                }

                data.append(row)

    df = pd.DataFrame(data)
    print(df.head())
    save_csv(data, prefix="suppliers", name="supplier_logs")

if __name__ == "__main__":
    generate_and_save_supply_orders()
    print("Supplier logs generated successfully!")
