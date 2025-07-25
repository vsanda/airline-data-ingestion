import sys
import os
import random
from collections import defaultdict
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Project utilities & static data
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.load_utils import load_dim_flights
from utils.save_utils import save_csv
from data.static.dim_crew import dim_crew
from data.static.dim_aircraft import dim_aircraft

# Load environment variables (e.g., for database connection)
load_dotenv()

fake = Faker()
engine = create_engine(os.getenv("POSTGRES_URL"))

def load_flights_from_postgres(engine, table_name="dim_flights"):
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, con=engine)
    return df

dim_flights = load_flights_from_postgres(engine)
dim_flights_df = pd.DataFrame(dim_flights)
print(dim_flights_df.head())
aircraft_fa_lookup = {a["aircraft_id"]: a["min_flight_attendants"] for a in dim_aircraft}

role_hours = {"Captain": 75, "First Officer": 80, "Flight Attendant": 100}

def get_duration_multiplier(flight_hours: float) -> float:
    if flight_hours >= 8:
        return 2.0
    elif flight_hours >= 5:
        return 1.6
    elif flight_hours >= 3:
        return 1.3
    else:
        return 1.2

def generate_duty_log(flight_id, crew, hourly_rate):

    #Get the flight record
    flight_row = dim_flights_df[dim_flights_df["flight_id"] == flight_id].iloc[0]

    #Parse flight info
    flight_day = flight_row["flight_day"]
    departure_time = datetime.fromisoformat(flight_row["departure_time"])
    arrival_time = datetime.fromisoformat(flight_row["arrival_time"])
    duty_start = departure_time - timedelta(hours=1)
    duty_end = arrival_time + timedelta(hours=1)
    duration = round((duty_end - duty_start).total_seconds() / 3600, 2)
    duration_multiplier = get_duration_multiplier(duration)

    # Crew flagged = True only if delayed and due to crew
    is_delayed = flight_row.get("status", False)
    delay_reason = flight_row.get("delay_reason", None)
    crew_flagged = bool(is_delayed and delay_reason == "crew")

    return {
        "flight_id": flight_id,
        "flight_day": flight_day,
        "hours_logged": duration,
        "duty_start": duty_start,
        "duty_end": duty_end,
        "hourly_rate_usd": hourly_rate * duration_multiplier,
        "crew_flagged": crew_flagged,
        "recorded_at": datetime.utcnow().isoformat(),
        "crew_id": crew["crew_id"],
        "name": crew["name"],
        "role": crew["role"],
        "base_location": crew["base_location"]
    }

def save_daily_crew(flight_day, data, output_dir="data/raw/crew"):
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/payroll_data_{flight_day.strftime('%Y%m%d')}.csv"
    data = pd.DataFrame(data)
    data.to_csv(filename, index=False)
    print(f"Saved {len(data)} flights to {filename}")

def save_sample_data(sample_df, output_dir="data/raw/crew"):
    os.makedirs(output_dir, exist_ok=True)
    today = datetime.today()
    filename = f"{output_dir}/payroll_data_{today.strftime('%Y%m%d')}.csv"
    sample_df.to_csv(filename, index=False)
    print(f"Saved sample {len(sample_df)} payroll data to {filename}")

def save_payroll_to_postgres(df, engine, table_name="payroll_data"):
    df = pd.DataFrame(df)
    df.to_sql(table_name, con=engine, if_exists="append", index=False)
    print(f"Loaded {len(df)}  to {table_name} in Postgres")

def generate_payroll():
    print("Generating daily crew logs...")
    logs_by_day = defaultdict(list)

    for _, row in dim_flights_df.iterrows():
        flight_id = row["flight_id"]
        aircraft_id = row["aircraft_id"]
        flight_day = datetime.strptime(row["flight_day"], '%Y-%m-%d').date()
        fa_count = aircraft_fa_lookup.get(aircraft_id, 2)

        for role, count in [("Captain", 1), ("First Officer", 1), ("Flight Attendant", fa_count + 1)]:
            candidates = [c for c in dim_crew if c["role"] == role]
            sampled_crew = random.sample(candidates, count)
            for crew in sampled_crew:
                monthly_salary = crew["salary_usd"] / 12
                hourly_rate = round(monthly_salary / role_hours[role], 2)
                log = generate_duty_log(flight_id, crew, hourly_rate)
                logs_by_day[flight_day].append(log)

    # # save per day
    # for flight_day, logs in logs_by_day.items():
    #     save_daily_crew(flight_day, logs)

    all_logs = [log for day_logs in logs_by_day.values() for log in day_logs]
    all_data = pd.DataFrame(all_logs)
    print(f"Total crew logs: {len(all_data)}")
    sample_df = pd.DataFrame(all_data).head(10)
    save_sample_data(sample_df)
    save_payroll_to_postgres(all_data, engine)

if __name__ == "__main__":

    generate_payroll()
