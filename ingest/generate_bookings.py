import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from faker import Faker
import random
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
import json
from data.static.dim_aircraft import dim_aircraft
from utils.load_utils import load_dim_flights
from utils.save_utils import save_csv
from sqlalchemy import create_engine
from dotenv import load_dotenv

engine = create_engine(os.getenv("POSTGRES_URL"))
fake = Faker()

def load_flights_from_postgres(engine, table_name="dim_flights"):
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, con=engine)
    return df

# import directly from postgres
dim_flights_df = load_flights_from_postgres(engine)
dim_aircraft_df = pd.DataFrame(dim_aircraft)
merged_df = dim_flights_df.merge(dim_aircraft_df, on='aircraft_id', how='left')
print(dim_flights_df.head())

price_ranges = {
    "Regional Jet": (120, 200),
    "Narrow-body": (200, 450),
    "Wide-body": (600, 900)
}

segment_multiplier = {
    "economy": 0.8,
    "premium_economy": 1.0,
    "business": 1.2,
}

segment_weights = {
    "economy": 0.75,
    "premium_economy": 0.15,
    "business": 0.10
}

per_hour_rate = {
    "Regional Jet": 35,
    "Narrow-body": 45,
    "Wide-body": 60
}

def weighted_customer_segment():
    segments = list(segment_weights.keys())
    weights = list(segment_weights.values())
    return random.choices(segments, weights=weights, k=1)[0]

def get_random_price(aircraft_type: str, segment: str, duration_hours: float) -> float:
    hourly_rate = per_hour_rate.get(aircraft_type, 100)  
    multiplier = segment_multiplier.get(segment, 1.0)
    base_price = duration_hours * hourly_rate * multiplier
    jitter = random.uniform(0.8, 1.2)
    return round(base_price * jitter, 2)

def realistic_passenger_count(capacity, flight_hours):
    if flight_hours < 2:
        return random.randint(int(capacity * 0.85), capacity)
    elif flight_hours < 5:
        return random.randint(int(capacity * 0.70), int(capacity * 0.85))
    else:
        return random.randint(int(capacity * 0.50), int(capacity * 0.65))
    
def save_daily_bookings(flight_day, data, output_dir="data/raw/bookings"):
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/passenger_data_{flight_day.strftime('%Y%m%d')}.csv"
    data.to_csv(filename, index=False)
    print(f"Saved {len(data)} flights to {filename}")

def save_sample_data(sample_df, output_dir="data/raw/bookings"):
    os.makedirs(output_dir, exist_ok=True)
    today = datetime.today()
    filename = f"{output_dir}/passenger_data_{today.strftime('%Y%m%d')}.csv"
    sample_df.to_csv(filename, index=False)
    print(f"Saved sample {len(sample_df)} bookings to {filename}")

def save_bookings_to_postgres(df, engine, table_name="passenger_data"):
    df = pd.DataFrame(df)
    df.to_sql(table_name, con=engine, if_exists="append", index=False)
    print(f"Loaded {len(df)} bookings to {table_name} in Postgres")


def generate_bookings():
    data_by_day = defaultdict(list)

    for _, row in merged_df.iterrows():
        flight_id = row["flight_id"]
        aircraft_id = row["aircraft_id"]
        departure_time = row["departure_time"]
        aircraft_type = row["aircraft_type"]
        capacity = row["max_capacity"]

        #calculate duration from dim flights
        departure_time = datetime.fromisoformat(row["departure_time"])
        if isinstance(departure_time, str):
            departure_time = datetime.fromisoformat(departure_time)
        flight_day = datetime.fromisoformat(row["flight_day"])
        arrival_time = datetime.fromisoformat(row["arrival_time"])
        duty_start = departure_time - timedelta(hours=1)
        duty_end = arrival_time + timedelta(hours=1)
        duration = round((duty_end - duty_start).total_seconds() / 3600, 2)
        # departure_dt = datetime.fromisoformat(departure_time)

        passenger_count = realistic_passenger_count(capacity, duration)
        booking_time_base = departure_time - timedelta(days=random.randint(5, 30))

        for _ in range(passenger_count):
            booking_time = booking_time_base - timedelta(minutes=random.randint(0, 1440))  # up to 1 day earlier

            segment = weighted_customer_segment()
            ticket_price = get_random_price(aircraft_type, segment, duration)

            data_by_day[flight_day].append({
                "booking_id": fake.uuid4(),
                "passenger_name": fake.name(),
                "flight_id": flight_id,
                "aircraft_id": aircraft_id,
                "departure_time": departure_time,
                "seat_number": fake.bothify("##?"),
                "booking_time": booking_time.isoformat(),
                "booking_status": random.choices(["confirmed", "cancelled", "checked_in"], weights=[70, 2, 28])[0],
                "ticket_price": ticket_price,
                "baggage_fee": round(random.uniform(0, 100), 2),
                "upgrades": random.choice([0, 50, 100, 150]),
                "channel": random.choice(["website", "travel_agent", "app"]),
                "customer_segment": segment,
                "aircraft_type": aircraft_type,
                "currency": "USD",
                "flight_day": flight_day,
                "recorded_at": datetime.utcnow().isoformat()
            })

    # #save per day
    # for flight_day, bookings in data_by_day.items():
    #     bookings = pd.DataFrame(bookings)
    #     save_daily_bookings(flight_day, bookings)
    

    # Print sample stats
    all_data = [b for day_data in data_by_day.values() for b in day_data]
    print(f"Total bookings: {len(all_data)}")
    sample_df = pd.DataFrame(all_data).head(10)
    save_sample_data(sample_df)
    # avg_price_per_flight = sample_df["ticket_price"].mean()
    # print("sample average ticket price:", avg_price_per_flight)
    print(sample_df.head())
    save_bookings_to_postgres(all_data, engine)

if __name__ == "__main__":
    generate_bookings()




