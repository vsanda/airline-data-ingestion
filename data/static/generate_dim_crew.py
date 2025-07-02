from faker import Faker
import random
import json

fake = Faker()
Faker.seed(42)
random.seed(42)

base_locations = ["JFK", "SFO", "ATL", "SEA", "BOS"]

crew_config = {
    "Captain": {"prefix": "CR1", "count": 15, "salary_range": (250000, 280000)},
    "First Officer": {"prefix": "CR2", "count": 15, "salary_range": (150000, 175000)},
    "Flight Attendant": {"prefix": "CR3", "count": 28, "salary_range": (70000, 90000)}
}

dim_crew = []
crew_id_counter = {
    "Captain": 1,
    "First Officer": 1,
    "Flight Attendant": 1
}

for role, config in crew_config.items():
    for _ in range(config["count"]):
        crew_id = f"{config['prefix']}{str(crew_id_counter[role]).zfill(3)}"
        name = fake.unique.name()
        base = random.choice(base_locations)
        salary = random.randint(*config["salary_range"])

        dim_crew.append({
            "crew_id": crew_id,
            "name": name,
            "role": role,
            "base_location": base,
            "salary_usd": salary
        })

        crew_id_counter[role] += 1

# Save to dim_crew.py
with open("data/static/dim_crew.py", "w") as f:
    f.write("dim_crew = ")
    json.dump(dim_crew, f, indent=4)

print(f"Saved {len(dim_crew)} crew members: 15 Captains, 15 FOs, 28 FAs.")
