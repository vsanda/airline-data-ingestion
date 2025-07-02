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
from utils.load_utils import load_dim_flights
import random
import json
from faker import Faker

fake = Faker()

# Load airport codes from JSON file
json_path = os.path.join("data", "keys", "airport_codes.json")
with open(json_path, "r") as f:
    airport_codes = json.load(f)

dim_flights = load_dim_flights()
dim_flights_df = pd.DataFrame(dim_flights)
dim_flights_df["flight_day"] = pd.to_datetime(dim_flights_df["flight_day"]).dt.date

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

def save_daily_flights(flight_day, data, output_dir="data/raw/flights"):
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/flights_data_{flight_day.strftime('%Y%m%d')}.csv"
    data = pd.DataFrame(data)
    data.to_csv(filename, index=False)
    print(f"Saved {len(data)} flights to {filename}")

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

    df_live = pd.DataFrame(data["states"], columns=columns)
    df_live["timestamp"] = datetime.utcfromtimestamp(data["time"]).isoformat()

    dim_routes_df = pd.DataFrame(dim_routes)
    # df = df.head(len(dim_flights_df))
    
    for day in sorted(dim_flights_df["flight_day"].unique()):
        flights_for_day = dim_flights_df[dim_flights_df["flight_day"] == day].reset_index(drop=True)
        n = len(flights_for_day)

        day_df = df_live.sample(n=n, replace=True).reset_index(drop=True) # Trim or sample OpenSky live data to match flight count
        day_df["flight_id"] = flights_for_day['flight_id'].values 
        # day_df["flight_day"] = day 

        day_df = day_df.merge(flights_for_day,on="flight_id",how="left")
        day_df = day_df.merge(dim_routes_df, on="route_id", how="left")

        save_daily_flights(day, day_df)      


    # ### ✨ ADDITIONAL FIELDS FOR P&L MODELING ✨ ###
    # df["flight_id"] =  dim_flights_df["flight_id"].values[:len(df)]

    # ### merging with dim flights and dim routes
    # df = df.merge(dim_flights_df[["flight_id", "route_id", "aircraft_id", "flight_day", "departure_time", "arrival_time", "status", "delay_reason", "delay_minutes", "fixed_cost"]],on="flight_id",how="left")
    # df = df.merge(dim_routes_df[["route_id", "origin_airport_code", "destination_airport_code", "distance_miles", "region", "route_category", "flight_time_minutes"]], on="route_id", how="left")

    # ### SAVE TO CSV ###
    # save_csv(df, prefix="flights", name="flights")
    # print(df.head())

if __name__ == "__main__":
    fetch_flight_data()
