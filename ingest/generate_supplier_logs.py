import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
import pandas as pd
import os
import json
from faker import Faker
import uuid
import math
from random import choice, randint, uniform
from collections import defaultdict
from datetime import datetime as dt
from data.static.dim_suppliers import dim_suppliers
# from data.static.dim_flights import dim_flights
from data.static.dim_aircraft import dim_aircraft
from utils.load_utils import load_dim_flights
from utils.save_utils import save_csv
import random

fake = Faker()

print("Simulating supplier logs...")

dim_flights = load_dim_flights()
dim_flights_df = pd.DataFrame(dim_flights)
dim_aircraft_df = pd.DataFrame(dim_aircraft)
merged_df = dim_flights_df.merge(dim_aircraft_df, on='aircraft_id', how='left')

def save_daily_supply(flight_day, data, output_dir="data/raw/suppliers"):
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/supplier_logs_{flight_day.strftime('%Y%m%d')}.csv"
    data = pd.DataFrame(data)
    data.to_csv(filename, index=False)
    print(f"Saved {len(data)} flights to {filename}")

def generate_supply_orders():
    print("Generating supplier orders...")
    data_by_day = defaultdict(list)

    # Pre-filter suppliers by service type
    fuel_suppliers = [s for s in dim_suppliers if s["service_type"] == "Fuel"]
    maintenance_suppliers = [s for s in dim_suppliers if s["service_type"] == "Maintenance"]
    catering_suppliers = [s for s in dim_suppliers if s["service_type"] == "Catering"]

    for _, row in merged_df.iterrows():
        flight_id = row["flight_id"]
        aircraft_id = row["aircraft_id"]
        capacity = row["max_capacity"]
        flight_day = row["flight_day"]

        if isinstance(flight_day, str):
            flight_day = datetime.strptime(flight_day, '%Y-%m-%d').date()

        departure_time = datetime.fromisoformat(row["departure_time"])
        arrival_time = datetime.fromisoformat(row["arrival_time"])
        flight_hours = (arrival_time - departure_time).total_seconds() / 3600

        is_delayed = row.get("status", False)
        delay_reason = row.get("delay_reason", None)
        supplier_flagged = bool(is_delayed and delay_reason == "supplier")

        services_needed = []
        if fuel_suppliers:
            services_needed.append(("Fuel", random.choice(fuel_suppliers)))
        if maintenance_suppliers:
            services_needed.append(("Maintenance", random.choice(maintenance_suppliers)))
        if catering_suppliers:
            services_needed.append(("Catering", random.choice(catering_suppliers)))

        for service_type, supplier_info in services_needed:
            cost_usd = 0

            if service_type == "Fuel":
                base_fee = 400
                size_multiplier = 1.3 if capacity > 200 else 1.0
                duration_multiplier = round(1 + 0.85 * flight_hours * random.uniform(0.9, 1.2))
                cost_usd = round(base_fee * size_multiplier * duration_multiplier * random.uniform(0.9, 1.2), 2)

            elif service_type == "Maintenance":
                base_cost = 3500
                multiplier = 2.0 if capacity > 200 else 1.0
                duration_factor = min(math.pow(1.2, flight_hours), 3.0)
                cost_usd = round(base_cost * multiplier * duration_factor * random.uniform(0.9, 1.2), 2)

            elif service_type == "Catering":
                base_per_passenger = random.uniform(20, 30)
                if flight_hours >= 8:
                    duration_multiplier = 2.0
                elif flight_hours >= 5:
                    duration_multiplier = 1.6
                elif flight_hours >= 3:
                    duration_multiplier = 1.3
                else:
                    duration_multiplier = 1.0
                cost_usd = round(base_per_passenger * capacity * duration_multiplier * random.uniform(0.9, 1.2), 2)

            order = {
                "order_id": "ORD-" + str(uuid.uuid4())[:8],
                "supplier_id": supplier_info["supplier_id"],
                "supplier": supplier_info["name"],
                "service_type": service_type,
                "flight_id": flight_id,
                "aircraft_id": aircraft_id,
                "order_date": fake.date_between(start_date='-30d', end_date='today').isoformat(),
                "expected_delivery": fake.date_between(start_date='today', end_date='+15d').isoformat(),
                "supplier_flagged": supplier_flagged,
                "cost_usd": cost_usd,
                "flight_day": flight_day,
                "recorded_at": datetime.utcnow().isoformat()
            }

            data_by_day[flight_day].append(order)

    # Save per day
    for flight_day, day_data in data_by_day.items():
        save_daily_supply(flight_day, day_data)

    all_data = [order for day_orders in data_by_day.values() for order in day_orders]
    df = pd.DataFrame(all_data)
    print(df.head())
    print("Total cost per flight:", df.groupby("flight_id")["cost_usd"].sum().reset_index(name="total_supplier_cost"))
    # save_csv(data, prefix="suppliers", name="supplier_logs")

if __name__ == "__main__":
    generate_supply_orders()
    print("Supplier logs generated successfully!")
