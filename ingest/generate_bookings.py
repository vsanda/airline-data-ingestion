import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from faker import Faker
import random
from datetime import datetime, timedelta
import pandas as pd
import json
from data.static.dim_aircraft import dim_aircraft
from data.static.dim_flights import dim_flights
from utils.save_utils import save_csv

fake = Faker()

dim_flights_df = pd.DataFrame(dim_flights)
dim_aircraft_df = pd.DataFrame(dim_aircraft)
merged_df = dim_flights_df.merge(dim_aircraft_df, on='aircraft_id', how='left')

def generate_and_save():
    data = []

    for _, row in merged_df.iterrows():
        flight_id = row["flight_id"]
        aircraft_id = row["aircraft_id"]
        departure_time = row["departure_time"]
        flight_day = row["flight_day"]
        aircraft_type = row["aircraft_type"]
        capacity = row["max_capacity"]
        departure_dt = datetime.fromisoformat(departure_time)
        passenger_count = random.randint(int(capacity * 0.7), int(capacity * 0.95))
        booking_time_base = departure_dt - timedelta(days=random.randint(5, 30))

        for _ in range(passenger_count):
            booking_time = booking_time_base - timedelta(minutes=random.randint(0, 1440))  # up to 1 day earlier
            data.append({
                "booking_id": fake.uuid4(),
                "passenger_name": fake.name(),
                "flight_id": flight_id,
                "aircraft_id": aircraft_id,
                "departure_time": departure_time,
                "seat_number": fake.bothify("##?"),
                "booking_time": booking_time.isoformat(),
                "booking_status": random.choices(["confirmed", "cancelled", "checked_in"], weights=[70, 2, 28])[0],
                "ticket_price": round(random.uniform(150, 1200), 2),
                "baggage_fee": round(random.uniform(0, 100), 2),
                "upgrades": random.choice([0, 50, 100, 150]),
                "channel": random.choice(["website", "travel_agent", "app"]),
                "customer_segment": random.choice(["business", "economy", "premium_economy"]),
                "aircraft_type": aircraft_type,
                "currency": "USD",
                "flight_day": flight_day,
                "recorded_at": datetime.utcnow().isoformat()
            })

    df = pd.DataFrame(data)
    print(df.head())
    save_csv(data, prefix="bookings", name="passenger_data")

if __name__ == "__main__":
    generate_and_save()




