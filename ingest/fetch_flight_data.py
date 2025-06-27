import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from pathlib import Path
import requests
import os
from datetime import datetime,timedelta
from utils.save_utils import save_csv
from data.static.dim_routes import dim_routes
from data.static.dim_flights import dim_flights
import random
import json
from faker import Faker

fake = Faker()

# Load airport codes from JSON file
json_path = os.path.join("data", "keys", "airport_codes.json")
with open(json_path, "r") as f:
    airport_codes = json.load(f)


def get_opensky_access_token():
    token_url = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"

    response = requests.post(token_url, data={
        "grant_type": "client_credentials",
        "client_id": os.getenv("OPENSKY_CLIENT_ID"),
        "client_secret": os.getenv("OPENSKY_CLIENT_SECRET")
    }, headers={
        "Content-Type": "application/x-www-form-urlencoded"
    })

    if response.status_code != 200:
        raise Exception(f"Token request failed: {response.status_code} - {response.text}")

    print(response.json()["access_token"])
    return response.json()["access_token"]

def fetch_flight_data():
    print("Fetching flight data from OpenSky...")

    token = get_opensky_access_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Optional: bounding box for efficiency
    url = "https://opensky-network.org/api/states/all?lamin=35.0&lomin=-10.0&lamax=60.0&lomax=30.0"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Flight data request failed: {response.status_code} - {response.text}")

    data = response.json()

    if "states" not in data or not data["states"]:
        print("No live flight data received.")
        return

    columns = [
        "icao24", "callsign", "origin_country", "time_position", "last_contact", "longitude",
        "latitude", "baro_altitude", "on_ground", "velocity", "heading", "vertical_rate",
        "sensors", "geo_altitude", "squawk", "spi", "position_source"
    ]

    df = pd.DataFrame(data["states"], columns=columns)
    df["timestamp"] = datetime.utcfromtimestamp(data["time"]).isoformat()

    dim_flights_df = pd.DataFrame(dim_flights)
    dim_routes_df = pd.DataFrame(dim_routes)
    df = df.head(len(dim_flights_df))

    ### ✨ ADDITIONAL FIELDS FOR P&L MODELING ✨ ###
    df["flight_id"] =  dim_flights_df["flight_id"].values[:len(df)]

    ### merging with dim flights and dim routes
    df = df.merge(dim_flights_df[["flight_id", "route_id", "aircraft_id", "flight_day", "departure_time", "arrival_time"]],on="flight_id",how="left")
    df = df.merge(dim_routes_df[["route_id", "origin_airport_code", "destination_airport_code", "distance_miles", "region", "route_category", "flight_time_minutes"]], on="route_id", how="left")

    # Simulate aircraft and pilot IDs
    df["status"] = ["delayed" if random.random() < 0.3 else "on-time" for _ in range(len(df))]
    df["delay_minutes"] = df["status"].apply(lambda x: random.randint(0, 120) if x == "delayed" else 0)

    ### SAVE TO CSV ###
    save_csv(df, prefix="flights", name="flights")
    print(df.head())

if __name__ == "__main__":
    fetch_flight_data()
