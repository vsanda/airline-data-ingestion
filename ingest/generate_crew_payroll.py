import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from faker import Faker
import random
import uuid
from datetime import timedelta, datetime
from utils.save_utils import save_json
from datetime import datetime
import pandas as pd
import json

fake = Faker()

# Load flight IDs from JSON file
json_path = os.path.join("data", "keys", "flight_ids.json")
with open(json_path, "r") as f:
    flight_ids = json.load(f)

used_ids = set()
def generate_unique_crew_id():
    while True:
        crew_id = f"CR-{random.randint(1000, 9999)}"
        if crew_id not in used_ids:
            used_ids.add(crew_id)
            return crew_id


def generate_crew_profile(role, base_salary, role_avg_hours):
    crew_id = generate_unique_crew_id()
    name = fake.unique.name()
    monthly_salary = round(base_salary[role] + random.uniform(-5000, 5000), 2) / 12
    hourly_rate = round(monthly_salary / role_avg_hours[role], 2)

    return {
        "crew_id": crew_id,
        "name": name,
        "role": role,
        "monthly_salary_usd": monthly_salary,
        "hourly_rate_usd": hourly_rate
    }

def generate_duty_log(flight_id, role, salary, hourly_rate):
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
        "crew_flagged": random.choice([True, False]),
        "recorded_at": datetime.utcnow().isoformat()
    }


def generate_and_save(n=100):
    print("Generating daily crew logs...")

    base_salary = {"Pilot": 120000, "Co-Pilot": 90000, "Flight Attendant": 60000}
    role_avg_hours = {"Pilot": 120, "Co-Pilot": 180, "Flight Attendant": 220}
    data = []

    # Assume 1 pilot, 1 co-pilot, 2 attendants per flight
    roles_per_flight = [("Pilot", 1), ("Co-Pilot", 1), ("Flight Attendant", 2)]

    for flight_id in flight_ids:
        for role, count in roles_per_flight:
            for _ in range(count):
                profile = generate_crew_profile(role, base_salary, role_avg_hours)
                print(profile)
                log = generate_duty_log(flight_id, role, profile["monthly_salary_usd"], profile["hourly_rate_usd"])
                data.append({**profile, **log})

    df = pd.DataFrame(data)
    print(df.head())

    save_json(data, prefix="crew", name="payroll_data")

if __name__ == "__main__":
    generate_and_save()
