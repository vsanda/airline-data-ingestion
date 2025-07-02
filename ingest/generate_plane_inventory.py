import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from faker import Faker
import random
from utils.save_utils import save_json
from data.static.dim_aircraft import dim_aircraft
from datetime import datetime
import json

fake = Faker()

# Load flight IDs from JSON file
json_path = os.path.join("data", "keys", "aircraft_ids.json")
with open(json_path, "r") as f:
    aircraft_ids = json.load(f)

def generate_aircraft():
    data = []

    for aircraft in dim_aircraft:
        year_built = random.randint(2005, 2022)

        data.append({
            "aircraft_id": aircraft["aircraft_id"],
            "model": aircraft["model"],
            "manufacturer": "Airbus" if aircraft["model"].startswith("Airbus") else "Boeing",
            "aircraft_type": aircraft["aircraft_type"],
            "year_built": year_built,
            "capacity": aircraft["max_capacity"],
            "status": "active",
            "fuel_efficiency_gph": aircraft["fuel_burn_gph"],
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        })


    save_json(data, prefix="plane", name="inventory_data")

if __name__ == "__main__":
    generate_aircraft()
