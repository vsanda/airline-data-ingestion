import os
import requests
import pandas as pd
import random
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

EIA_API_KEY = os.getenv("EIA_API_KEY")

def generate_price(row):
    if "Jet Fuel" in row["product-name"]:
        return round(random.uniform(1.50, 4.50), 3)
    elif "Diesel" in row["product-name"]:
        return round(random.uniform(1.80, 5.00), 3)
    elif "Gasoline" in row["product-name"]:
        return round(random.uniform(1.60, 4.00), 3)
    elif "WTI" in row["product-name"] or "Brent" in row["product-name"]:
        return round(random.uniform(60, 120), 2)  # Dollars per barrel
    else:
        return round(random.uniform(1.00, 6.00), 3)


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
    df["price_per_gallon"] = df.apply(generate_price, axis=1)
    print(df.head())

    today = datetime.utcnow().strftime("%Y-%m-%d")
    output_path = Path(f"data/raw/fuel/crude_oil_prices_{today}.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Saved {len(df)} jet fuel price records to {output_path}")
    
if __name__ == "__main__":
    fetch_fuel_prices()