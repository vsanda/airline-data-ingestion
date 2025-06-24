import pandas as pd
from pathlib import Path
import requests
import os
from datetime import datetime

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

    today = datetime.utcnow().strftime("%Y-%m-%d")
    output_path = Path(f"data/raw/flights/flights_{today}.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    df.head()

    print(f"Saved {len(df)} live flight records to {output_path}")

if __name__ == "__main__":
    fetch_flight_data()
