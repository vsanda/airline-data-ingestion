import random
import json

# 5 Domestic and 2 International Routes (No Haneda)
domestic_routes = [
    ("JFK", "LAX"),  # 2475 mi
    ("SFO", "ORD"),  # 1846 mi
    ("ATL", "DFW"),  # 732 mi
    ("SEA", "DEN"),  # 1024 mi
    ("BOS", "MIA")   # 1258 mi
]

international_routes = [
    ("JFK", "CDG"),  # Paris – 3625 mi
    ("SFO", "SIN")   # Singapore – 8446 mi
]

# Distance map
distances = {
    ("JFK", "LAX"): 2475,
    ("SFO", "ORD"): 1846,
    ("ATL", "DFW"): 732,
    ("SEA", "DEN"): 1024,
    ("BOS", "MIA"): 1258,
    ("JFK", "CDG"): 3625,
    ("SFO", "SIN"): 8446
}

def estimate_duration_mins(distance):
    avg_speed_mph = 500
    return int((distance / avg_speed_mph) * 60)

def get_category(distance):
    if distance < 1000:
        return "Short-haul"
    elif distance < 3000:
        return "Medium-haul"
    else:
        return "Long-haul"

dim_routes = []

for origin, dest in domestic_routes + international_routes:
    distance = distances[(origin, dest)]
    duration = estimate_duration_mins(distance)
    category = get_category(distance)
    region = "Domestic" if category in ["Short-haul", "Medium-haul"] else "International"

    dim_routes.append({
        "route_id": f"RT{random.randint(1000, 9999)}",
        "origin_airport_code": origin,
        "destination_airport_code": dest,
        "distance_miles": distance,
        "region": region,
        "route_category": category,
        "flight_time_minutes": duration
    })


with open("data/static/dim_routes.py", "w") as f:
    f.write("dim_routes = ")
    json.dump(dim_routes, f, indent=4)

print("Successfully saved 7 routes: 5 domestic + 2 international (no HND).")
