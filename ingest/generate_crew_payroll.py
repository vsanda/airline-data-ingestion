from faker import Faker
import random
from utils.save_utils import save_json
from datetime import datetime

fake = Faker()

def generate_and_save(n=20):
    data = []
    for _ in range(n):
        role = random.choice(["Pilot", "Co-Pilot", "Flight Attendant"])
        base_salary = {"Pilot": 120000, "Co-Pilot": 90000, "Flight Attendant": 60000}[role]
        data.append({
            "crew_id": fake.uuid4(),
            "name": fake.name(),
            "role": role,
            "hours_logged": random.randint(50, 200),
            "monthly_salary": round(base_salary + random.uniform(-5000, 5000), 2),
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        })
    save_json(data, prefix="crew", name="payroll_data")

if __name__ == "__main__":
    generate_and_save()
