from faker import Faker
import random
import json

fake = Faker()
# random.seed(42)

base_locations = ["JFK", "SFO", "ATL", "SEA", "BOS"]

service_types = {
    "Fuel": (1, 3),
    "Maintenance": (3, 6),
    "Catering": (2, 5)
}

dim_suppliers = []
supplier_id_counter = 1

def generate_supplier_name(service_type):
    base_name = fake.company() 
    if service_type == "Fuel":
        suffix = random.choice([
            " JetFuel", " Aviation Energy", " Propulsion Ltd.", " Fuel Systems", " AeroFuel"
        ])
    elif service_type == "Maintenance":
        suffix = random.choice([
            " AeroTech", " Aircraft Maintenance", " Avionics Services", " Aviation Works", " AeroSystems"
        ])
    elif service_type == "Catering":
        suffix = random.choice([
            " Inflight Catering", " SkyMeals", " Cabin Cuisine", " JetBites", " CloudCatering"
        ])
    else:
        suffix = ""

    return f"{base_name}{suffix}"

for service_type, (min_n, max_n) in service_types.items():
    count = random.randint(min_n, max_n)
    for _ in range(count):
        supplier_id = f"S{str(supplier_id_counter).zfill(3)}"
        base = random.choice(base_locations)
        name = generate_supplier_name(service_type)

        dim_suppliers.append({
            "supplier_id": supplier_id,
            "name": name,
            "base_location": base,
            "service_type": service_type,
        })

        supplier_id_counter += 1

# Save to dim_suppliers.py
with open("data/static/dim_suppliers.py", "w") as f:
    f.write("dim_suppliers = ")
    json.dump(dim_suppliers, f, indent=4)

print(f"Saved {len(dim_suppliers)} suppliers.")
