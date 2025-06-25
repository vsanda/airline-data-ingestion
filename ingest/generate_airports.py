from faker import Faker
import random
from utils.save_utils import save_json
from datetime import datetime

fake = Faker()

def generate_and_save(n=15):
    data = []
    for _ in range(n):
        code = fake.unique.bothify(text="???").upper()
        data.append({
            "airport_code": code,
            "name": f"{fake.city()} International Airport",
            "city": fake.city(),
            "country": fake.country(),
            "timezone": fake.timezone(),
            "elevation_ft": random.randint(0, 10000),
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        })
    save_json(data, prefix="airports", name="airports_data")

if __name__ == "__main__":
    generate_and_save()
