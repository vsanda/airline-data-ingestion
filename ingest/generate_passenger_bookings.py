import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from faker import Faker
import random
from datetime import datetime, timedelta
import pandas as pd
import json
from utils.save_utils import save_json

fake = Faker()

# Load flight IDs from JSON file
json_path = os.path.join("data", "keys", "flight_ids.json")
with open(json_path, "r") as f:
    flight_ids = json.load(f)


def generate_and_save(n=200):
    data = []
    for _ in range(n):
        
        flight_id = random.choice(flight_ids)
        departure_time = fake.date_time_between(start_date='-30d', end_date='+30d')
        booking_time = departure_time - timedelta(days=random.randint(1, 30))

        base_price = round(random.uniform(150, 1200), 2)
        baggage_fee = round(random.uniform(0, 100), 2)
        upgrades = random.choice([0, 50, 100, 150])
        channel = random.choice(["website", "travel_agent", "app"])
        customer_segment = random.choice(["business", "economy", "premium_economy"])

        data.append({
            "booking_id": fake.uuid4(),
            "passenger_name": fake.name(),
            "flight_id": flight_id,
            "seat_number": fake.bothify("##?"),
            "departure_time": departure_time.isoformat(),
            "booking_time": booking_time.isoformat(),
            "booking_status": random.choice(["confirmed", "cancelled", "checked_in"]),
            "ticket_price": base_price,
            "flight_day": departure_time.date().isoformat(),
            "baggage_fee": baggage_fee,
            "upgrades": upgrades,
            "channel": channel,
            "customer_segment": customer_segment,
            "currency": "USD",
            "recorded_at": datetime.utcnow().isoformat()
        })

    df = pd.DataFrame(data)
    print(df.head())
    save_json(data, prefix="bookings", name="passenger_data")

if __name__ == "__main__":
    generate_and_save()



