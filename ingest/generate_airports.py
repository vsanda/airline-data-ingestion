import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from faker import Faker
import random
from utils.save_utils import save_json, save_keys
from datetime import datetime

fake = Faker()

def generate_and_save(n=15):
    data = []
    airport_codes = []

    for _ in range(n):
        code = fake.unique.bothify(text="???").upper()
        airport_codes.append(code)
        data.append({
            "airport_code": code,
            "name": f"{fake.city()} International Airport",
            "city": fake.city(),
            "country": fake.country(),
            "timezone": fake.timezone(),
            "elevation_ft": random.randint(0, 10000),
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        })

    # Save full airport data
    save_json(data, prefix="airports", name="airports_data")

    # Save just the codes as a separate key file
    save_keys(airport_codes, name="airport_codes")

if __name__ == "__main__":
    generate_and_save()
