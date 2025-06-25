from faker import Faker
import random
from utils.save_utils import save_json
from datetime import datetime

fake = Faker()

def generate_and_save(n=10):
    data = []
    for _ in range(n):
        data.append({
            "aircraft_id": fake.unique.bothify("N#####"),
            "model": random.choice(["A320", "B737", "A350", "B787"]),
            "manufacturer": random.choice(["Airbus", "Boeing"]),
            "capacity": random.randint(120, 350),
            "status": random.choice(["active", "maintenance", "retired"]),
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        })
    save_json(data, prefix="plane", name="inventory_data")

if __name__ == "__main__":
    generate_and_save()
