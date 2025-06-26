import os
import requests
import pandas as pd
import random
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta
import numpy as np
import json

load_dotenv()

EIA_API_KEY = os.getenv("EIA_API_KEY")

def generate_price(row):
    name = row.lower()

    if "jet fuel" in name or "kerosene" in name:
        return round(random.uniform(2.25, 4.25), 3)  # Jet fuel (per gallon)
    elif "diesel" in name:
        return round(random.uniform(2.00, 5.00), 3)  # Ultra-low sulfur diesel (per gallon)
    elif "gasoline" in name:
        return round(random.uniform(2.00, 4.00), 3)  # Regular gasoline (per gallon)
    elif "brent" in name or "west texas" in name:
        return round(random.uniform(70.00, 120.00), 2)  # Crude oil (per barrel)
    else:
        return round(random.uniform(1.50, 5.50), 3)  # Fallback for other fuel types
    
def classify_fuel(name):
    name = name.lower()
    if "kerosene" in name or "jet fuel" in name:
        return "jet_fuel"
    elif "diesel" in name:
        return "diesel"
    elif "gasoline" in name:
        return "gasoline"
    elif "crude" in name or "brent" in name or "wti" in name:
        return "crude_oil"
    else:
        return "other"
    
def random_flight_day():
    start_date = datetime.today() - timedelta(days=90)
    return (start_date + timedelta(days=random.randint(0, 90))).date()


def fetch_fuel_prices():
    print("Fetching fuel prices from EIA...")

    if not EIA_API_KEY:
        raise ValueError("EIA_API_KEY is not set in the environment.")

    url = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
    
    params = {
        "api_key": EIA_API_KEY,
        "data": ["value"],
        "start": "2024-01",
        "end": "2025-01",
        "frequency": "monthly",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "offset": 0,
        "length": 100
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"EIA API error: {response.status_code} - {response.text}")

    json_data = response.json()
    records = json_data["response"]["data"]
    if not records:
        print("No fuel price data found.")
        return
    
    print(f"Found {len(records)} records of fuel prices.")
    df = pd.DataFrame(records)
    print(df.head())

    # Define enrichment maps
    DEFAULT_PRODUCTS = ["EIA-WTI", "EIA-Brent", "EIA-Kerosene"]
    PRODUCT_NAMES = {
        "EIA-WTI": "West Texas Intermediate",
        "EIA-Brent": "Brent Crude",
        "EIA-Kerosene": "Jet Fuel (Kerosene Blend)"
    }
    PROCESS_NAMES = {
        "refined": "Refined Price",
        "blended": "Blended Price",
        "spot": "Spot Price"
    }
    REGIONS = ["Gulf Coast", "Midwest", "West Coast", "Rocky Mountains"]

    # Map product_name safely
    df["product"] = np.random.choice(DEFAULT_PRODUCTS, size=len(df))
    df["product_name"] = df["product"].map(PRODUCT_NAMES).fillna("Unknown Product")
    df["process_name"] = np.random.choice(list(PROCESS_NAMES.values()), size=len(df))
    df["region"] = np.random.choice(REGIONS, size=len(df))
    df["price_month"] = pd.to_datetime(df["period"], format="%Y-%m").dt.to_period("M").astype(str)
    print(df["product_name"])
    df["price_per_gallon_usd"] = df["product_name"].apply(generate_price)
    df["fuel_category"] = df["product_name"].apply(classify_fuel)
    df["flight_day"] = [random_flight_day() for _ in range(len(df))]
    print(df.head())

    today = datetime.utcnow().strftime("%Y-%m-%d")
    output_path = Path(f"data/raw/fuel/crude_oil_prices_{today}.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Saved {len(df)} enriched jet fuel price records to {output_path}")
    
if __name__ == "__main__":
    fetch_fuel_prices()