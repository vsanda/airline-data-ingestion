import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from faker import Faker
import random
from datetime import timedelta, datetime
from utils.save_utils import save_json
from data.static.dim_crew import dim_crew
from data.static.dim_flights import dim_flights
from datetime import datetime
import pandas as pd
import json

fake = Faker()

dim_flights_df = pd.DataFrame(dim_flights)

used_ids = set()
def generate_unique_crew_id():
    while True:
        crew_id = f"CR-{random.randint(1000, 9999)}"
        if crew_id not in used_ids:
            used_ids.add(crew_id)
            return crew_id

role_hours = {"Captain": 120, "First Officer": 180, "Flight Attendant": 220}

def generate_duty_log(flight_id, crew, hourly_rate):
    flight_day = fake.date_between(start_date="-5d", end_date="today")
    start_hour = random.randint(6, 14)
    duration = random.randint(4, 10)
    duty_start = datetime.combine(flight_day, datetime.min.time()) + timedelta(hours=start_hour)
    duty_end = duty_start + timedelta(hours=duration)

    return {
        "flight_id": flight_id,
        "flight_day": flight_day.isoformat(),
        "hours_logged": duration,
        "duty_start": duty_start.isoformat(),
        "duty_end": duty_end.isoformat(),
        "hourly_rate_usd": hourly_rate,
        "crew_flagged": random.random() < 0.25,
        "recorded_at": datetime.utcnow().isoformat(),
        "crew_id": crew["crew_id"],
        "name": crew["name"],
        "role": crew["role"],
        "base_location": crew["base_location"]
    }

def generate_and_save():
    print("Generating daily crew logs...")

    flight_ids = dim_flights_df["flight_id"].tolist()
    logs = []

    for flight_id in flight_ids:
        for role, count in [("Captain", 1), ("First Officer", 1), ("Flight Attendant", 2)]:
            candidates = [c for c in dim_crew if c["role"] == role]
            sampled_crew = random.sample(candidates, count)
            for crew in sampled_crew:
                monthly_salary = crew["salary_usd"] / 12
                hourly_rate = round(monthly_salary / role_hours[role], 2)
                log = generate_duty_log(flight_id, crew, hourly_rate)
                logs.append(log)

    df = pd.DataFrame(logs)
    print(df.head())
    save_json(logs, prefix="crew", name="payroll_data")

if __name__ == "__main__":
    generate_and_save()
