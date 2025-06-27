import pandas as pd
import random
from datetime import datetime, timedelta
from dim_aircraft import dim_aircraft
from dim_routes import dim_routes
import json

# Ensure both dim tables are DataFrames
aircraft_df = pd.DataFrame(dim_aircraft)
routes_df = pd.DataFrame(dim_routes)

# Number of synthetic flights
num_flights = 10
flights = []

for _ in range(num_flights):
    route = routes_df.sample(1).iloc[0]
    aircraft = aircraft_df.sample(1).iloc[0]

    flight_id = f"FL{random.randint(1000, 9999)}"
    route_id = route["route_id"]
    aircraft_id = aircraft["aircraft_id"]

    # Random flight_day within past 90 days
    flight_day = datetime.today().date() - timedelta(days=random.randint(0, 90))

    # Departure time between 4am and 10pm
    dep_hour = random.randint(4, 22)
    dep_minute = random.choice([0, 15, 30, 45])
    departure_time = datetime.combine(flight_day, datetime.min.time()) + timedelta(hours=dep_hour, minutes=dep_minute)

    # Flight duration in hours (1 to 8 hrs)
    duration_hours = round(random.uniform(1.0, 8.0), 2)
    arrival_time = departure_time + timedelta(hours=duration_hours)

    flights.append({
        "flight_id": flight_id,
        "route_id": route_id,
        "aircraft_id": aircraft_id,
        "flight_day": flight_day.isoformat(),
        "departure_time": departure_time.isoformat(),
        "arrival_time": arrival_time.isoformat()
    })

# Output DataFrame
with open("data/static/dim_flights.py", "w") as f:
    f.write("dim_flights = ")
    json.dump(flights, f, indent=4, default=str)
