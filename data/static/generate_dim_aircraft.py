import random
import pandas as pd
import json

# Preset aircraft models with specs
aircraft_models = [
    # Regional Jets
    {"model": "Embraer E175",         "aircraft_type": "Regional Jet", "capacity": (70, 88),   "fuel_burn_gph": 550,  "max_range": 2000, "min_fa": 2},
    {"model": "CRJ700",               "aircraft_type": "Regional Jet", "capacity": (66, 78),   "fuel_burn_gph": 500,  "max_range": 1378, "min_fa": 2},
    
    # Narrow-body
    {"model": "Boeing 737-800",       "aircraft_type": "Narrow-body",  "capacity": (150, 189), "fuel_burn_gph": 850,  "max_range": 2935, "min_fa": 4},
    {"model": "Airbus A320neo",       "aircraft_type": "Narrow-body",  "capacity": (150, 180), "fuel_burn_gph": 790,  "max_range": 3450, "min_fa": 4},
    {"model": "Boeing 757-200",       "aircraft_type": "Narrow-body",  "capacity": (180, 200), "fuel_burn_gph": 1000, "max_range": 3900, "min_fa": 4},
    {"model": "Airbus A321XLR",       "aircraft_type": "Narrow-body",  "capacity": (180, 206), "fuel_burn_gph": 890,  "max_range": 4700, "min_fa": 5},
    
    # Wide-body (long-haul capable)
    {"model": "Boeing 787-9",         "aircraft_type": "Wide-body",    "capacity": (250, 296), "fuel_burn_gph": 1400, "max_range": 7635, "min_fa": 6},
    {"model": "Airbus A350-900",      "aircraft_type": "Wide-body",    "capacity": (280, 325), "fuel_burn_gph": 1350, "max_range": 8500, "min_fa": 7},
    {"model": "Boeing 777-300ER",     "aircraft_type": "Wide-body",    "capacity": (300, 368), "fuel_burn_gph": 1600, "max_range": 7930, "min_fa": 7},
    {"model": "Airbus A350-1000",     "aircraft_type": "Wide-body",    "capacity": (350, 410), "fuel_burn_gph": 1450, "max_range": 8700, "min_fa": 8}
]

num_aircraft = 15
aircraft_list = []

for _ in range(num_aircraft):
    spec = random.choice(aircraft_models)

    aircraft_id = f"AC{random.randint(1000, 9999)}"
    capacity = random.randint(*spec["capacity"])

    aircraft = {
        "aircraft_id": aircraft_id,
        "model": spec["model"],
        "aircraft_type": spec["aircraft_type"],
        "max_capacity": capacity,
        "fuel_burn_gph": spec["fuel_burn_gph"],
        "max_range_miles": spec["max_range"],
        "min_flight_attendants": spec["min_fa"]
    }

    aircraft_list.append(aircraft)

with open("data/static/dim_aircraft.py", "w") as f:
    f.write("dim_aircraft = ")
    json.dump(aircraft_list, f, indent=4, default=str)

print("Successfully saved dim_aircraft.py")


