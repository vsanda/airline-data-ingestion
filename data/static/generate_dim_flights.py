import pandas as pd
import random
from datetime import datetime, timedelta
import os
from dim_aircraft import dim_aircraft
from dim_routes import dim_routes
import json

# Ensure both dim tables are DataFrames
aircraft_df = pd.DataFrame(dim_aircraft)
routes_df = pd.DataFrame(dim_routes)

# Number of synthetic flights
num_flights = random.randint(8, 12)
flights = []

route_category_map = {
    "Short-haul": ["Regional Jet", "Narrow-body"],
    "Medium-haul": ["Narrow-body"],
    "Long-haul": ["Wide-body"]
}

fixed_cost_map = {
    "Regional Jet": 3500,
    "Narrow-body": 5500,
    "Wide-body": 8500
}

# def sample_route_once(routes_df, used_routes, limited_route_id="RT1009"):
#     for _ in range(10):
#         route = routes_df.sample(1).iloc[0]
#         route_id = route["route_id"]
#         if route_id == limited_route_id and route_id in used_routes:
#             continue
#         if route_id == limited_route_id:
#             used_routes.add(route_id)

#         return route
#     return None


def generate_delay():
    delayed = random.choices([True, False], weights=[0.2, 0.8])[0]  
    if not delayed:
        return False, "", 0

    reason = random.choices(
        ["crew", "supplier", "weather"],
        weights=[0.35, 0.45, 0.15]
    )[0]

    delay_minutes = random.randint(10, 120) 
    return True, reason, delay_minutes

def calculate_fixed_cost(aircraft_type: str, flight_hours: float) -> float:
    base_cost = fixed_cost_map.get(aircraft_type, 3000)
    duration_multiplier = 1 + (0.15 * flight_hours)
    cost = base_cost * duration_multiplier * random.uniform(0.95, 1.1)
    return round(cost, 2)

def save_daily_flights(flight_day, flights, output_dir="data/static/dim_flights"):
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/dim_flights_{flight_day.strftime('%Y%m%d')}.json"
    with open(filename, "w") as f:
        json.dump(flights, f, indent=4, default=str)
    print(f"Saved {len(flights)} flights to {filename}")
        

# Copy aircraft_df so we can remove used aircraft
available_aircraft = aircraft_df.copy()

for offset in range(30):
    flight_day = datetime.today().date() - timedelta(days=offset)
    num_flights = random.randint(8, 12)
    daily_flights = []

    for _ in range(num_flights):
        route = routes_df.sample(1).iloc[0]
        flight_id = f"FL{random.randint(1000, 9999)}"
        route_id = route["route_id"]
        route_distance = route["distance_miles"]

        allowed_types = route_category_map.get(route["route_category"], [])

        # Filter only available aircraft that can handle the route distance
        valid_aircraft = available_aircraft[available_aircraft["aircraft_type"].isin(allowed_types)]
        valid_aircraft = valid_aircraft[valid_aircraft["max_range_miles"] >= route_distance]

        if valid_aircraft.empty:
            print(f"No available aircraft can handle route {route_id} ({route_distance} miles)")
            continue

        aircraft = valid_aircraft.sample(1).iloc[0]
        aircraft_id = aircraft["aircraft_id"]
        aircraft_type = aircraft["aircraft_type"]

        # # 🧼 Remove selected aircraft from the available pool
        # available_aircraft = available_aircraft[available_aircraft["aircraft_id"] != aircraft_id]

        # Flight day + departure + arrival logic
        # flight_day = datetime.today().date() - timedelta(days=random.randint(0, 90))
        dep_hour = random.randint(4, 22)
        dep_minute = random.choice([0, 15, 30, 45])

        # use route duration for realistic modeling

        departure_time = datetime.combine(flight_day, datetime.min.time()) + timedelta(hours=dep_hour, minutes=dep_minute)
        duration_minutes = route["flight_time_minutes"]
        hours = int(route["flight_time_minutes"] // 60)
        minutes = int(route["flight_time_minutes"] % 60)
        flight_hours = round(duration_minutes / 60, 2)
        arrival_time = departure_time + timedelta(hours=hours, minutes=minutes)
        fixed_cost = calculate_fixed_cost(aircraft_type, flight_hours)
        # arrival_time = departure_time + timedelta(minutes=duration_minutes)

        delayed, delay_reason, delay_minutes = generate_delay()

        daily_flights.append({
            "flight_id": flight_id,
            "route_id": route_id,
            "aircraft_id": aircraft_id,
            "flight_day": flight_day.isoformat(),
            "departure_time": departure_time.isoformat(),
            "arrival_time": arrival_time.isoformat(),
            "status": "delayed" if delayed else "on-time",
            "delay_reason": delay_reason,
            "delay_minutes": delay_minutes,
            "fixed_cost": fixed_cost
        })

    save_daily_flights(flight_day, daily_flights)

# save to a dataframe in python
# with open("data/static/dim_flights.py", "w") as f:
#     f.write("dim_flights = ")
#     json.dump(flights, f, indent=4, default=str)

# print(f"Saved {len(flights)} flights.")