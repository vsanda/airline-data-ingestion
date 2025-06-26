import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from faker import Faker
import random
from utils.save_utils import save_json
from datetime import datetime
import json

fake = Faker()

# Load flight IDs from JSON file
json_path = os.path.join("data", "keys", "aircraft_ids.json")
with open(json_path, "r") as f:
    aircraft_ids = json.load(f)

def generate_and_save():
    data = []

    for aircraft_id in aircraft_ids:
        year_built = random.randint(2005, 2022)
        model = random.choice(["A320", "B737", "A350", "B787"])
        aircraft_type = "Wide-body" if model in ["A350", "B787"] else "Narrow-body"

        if aircraft_type == "Wide-body":
            fuel_efficiency_gph = round(random.uniform(1000, 1500), 2)
        else: # Narrow-body
            fuel_efficiency_gph = round(random.uniform(500, 800), 2)

        data.append({
            "aircraft_id": aircraft_id,
            "model": random.choice(model),
            "manufacturer": "Airbus" if model.startswith("A") else "Boeing",
            "aircraft_type": aircraft_type,
            "year_built": year_built,
            "capacity": random.randint(120, 350),
            "status": random.choice(["active", "maintenance", "retired"]),
            "fuel_efficiency_gph": fuel_efficiency_gph,
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        })

    save_json(data, prefix="plane", name="inventory_data")

if __name__ == "__main__":
    generate_and_save()
