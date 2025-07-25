import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random
import json
import requests

import pandas as pd
from faker import Faker
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Project utilities & static data
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.save_utils import save_csv
from utils.load_utils import load_dim_flights
from data.static.dim_routes import dim_routes

# Load environment variables and create DB engine
load_dotenv()
engine = create_engine(os.getenv("POSTGRES_URL"))
fake = Faker()

# Loading data directly from postgres
def load_flights_from_postgres(engine, table_name="dim_flights"):
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, con=engine)
    return df

# Load airport codes from JSON file
json_path = os.path.join("data", "keys", "airport_codes.json")
with open(json_path, "r") as f:
    airport_codes = json.load(f)

# how to load directly from multiple CSV files
# dim_flights = load_dim_flights()
# dim_flights_df = pd.DataFrame(dim_flights)
# dim_flights_df["flight_day"] = pd.to_datetime(dim_flights_df["flight_day"]).dt.date

# import directly from postgres
dim_flights_df = load_flights_from_postgres(engine)
print(dim_flights_df.head())

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

def save_sample_data(sample_df, output_dir="data/raw/flights"):
    os.makedirs(output_dir, exist_ok=True)
    today = datetime.today()
    filename = f"{output_dir}/flights_data_{today.strftime('%Y%m%d')}.csv"
    sample_df.to_csv(filename, index=False)
    print(f"Saved sample {len(sample_df)} flights to {filename}")

def save_flights_to_postgres(flights, engine, table_name="flights"):
    df = pd.DataFrame(flights)
    df.to_sql(table_name, con=engine, if_exists="append", index=False)
    print(f"Loaded {len(df)} flights to {table_name} in Postgres")

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
    # df_live["timestamp"] = datetime.utcfromtimestamp(data["time"]).isoformat() - used dim_flights ingestion instead

    dim_routes_df = pd.DataFrame(dim_routes)
    # df = df.head(len(dim_flights_df))
    
    all_flights = []
    for day in sorted(dim_flights_df["flight_day"].unique()):
        flights_for_day = dim_flights_df[dim_flights_df["flight_day"] == day].reset_index(drop=True)
        n = len(flights_for_day)

        day_df = df_live.sample(n=n, replace=True).reset_index(drop=True) # Trim or sample OpenSky live data to match flight count
        day_df["flight_id"] = flights_for_day['flight_id'].values 
        # day_df["flight_day"] = day 

        day_df = day_df.merge(flights_for_day,on="flight_id",how="left")
        day_df = day_df.merge(dim_routes_df, on="route_id", how="left")

        # save_daily_flights(day, day_df)
        all_flights.extend(day_df.to_dict(orient="records"))      

    print(f"Total flights: {len(all_flights)}")
    sample_df = pd.DataFrame(all_flights).head(10)
    save_sample_data(sample_df)
    save_flights_to_postgres(all_flights, engine)

    # ### ✨ ADDITIONAL FIELDS FOR P&L MODELING ✨ ###
    # df["flight_id"] =  dim_flights_df["flight_id"].values[:len(df)]

if __name__ == "__main__":
    fetch_flight_data()
