import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from pathlib import Path
import requests
import os
from datetime import datetime,timedelta
from utils.save_utils import save_keys
import random
import json
from faker import Faker

fake = Faker()

# # Load flight IDs from JSON file
# json_path = os.path.join("data", "keys", "flight_ids.json")
# with open(json_path, "r") as f:
#     flight_ids = json.load(f)

# Load airport codes from JSON file
json_path = os.path.join("data", "keys", "airport_codes.json")
with open(json_path, "r") as f:
    airport_codes = json.load(f)

# Load aircraft ids from JSON file
json_path = os.path.join("data", "keys", "aircraft_ids.json")
with open(json_path, "r") as f:
    aircraft_ids = json.load(f)

def generate_flight_ids(n=10):
    return [f"FL{random.randint(0, 9999):04}" for _ in range(n)]



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
    df = df.head(5)

    ### ✨ ADDITIONAL FIELDS FOR P&L MODELING ✨ ###
    flight_ids = generate_flight_ids(5)
    df["flight_id"] =  random.choice(flight_ids)
    df["departure_time"] = [fake.date_time_between(start_date="-1d", end_date="+12h") for _ in range(len(df))]
    df["arrival_time"] = df["departure_time"].apply(lambda x: x + timedelta(hours=random.randint(1, 6)))

    # Simulate airport codes
    df["origin_airport_code"] = [random.choice(airport_codes) for _ in range(len(df))]
    df["destination_airport_code"] = [random.choice([code for code in airport_codes if code != origin]) for origin in df["origin_airport_code"]]
    df["route_id"] = df["origin_airport_code"] + "-" + df["destination_airport_code"]

    # Simulate aircraft and pilot IDs
    df["status"] = random.choices(["on-time", "delayed"], k=len(df))
    df["delay_minutes"] = df["status"].apply(lambda x: random.randint(0, 120) if x == "delayed" else 0)
    df["delay_cost"] = df["delay_minutes"] * random.uniform(25, 75)  
    df["route_id"] = df["origin_airport_code"] + "-" + df["destination_airport_code"]
    df["aircraft_id"] = [random.choice(aircraft_ids) for _ in range(len(df))]
    df["flight_day"] = df["departure_time"].apply(lambda x: x.date())

    ### SAVE TO CSV ###
    today = datetime.utcnow().strftime("%Y-%m-%d")
    output_path = Path(f"data/raw/flights/flights_{today}.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(df.head())

    ### SAVE TO JSON ###
    # Save just the codes as a separate key file
    save_keys(flight_ids, name="flight_ids")

    print(f"Saved {len(df)} live flight records to {output_path}")

if __name__ == "__main__":
    fetch_flight_data()
