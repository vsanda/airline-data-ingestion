import os
import pandas as pd
import glob
from sqlalchemy import create_engine
from dotenv import load_dotenv
import json

load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_URL")
engine = create_engine(POSTGRES_URL)

datasets = [
    {"prefix": "fuel", "name": "crude_oil_prices"},
    {"prefix": "flights", "name": "flights"},
    {"prefix": "suppliers", "name": "supplier_logs"},
]

def get_latest_file(prefix):
    files = glob.glob(f"data/raw/{ds['prefix']}/{ds['name']}_*.csv") + glob.glob(f"data/raw/{ds['prefix']}/{ds['name']}_*.json")
    print(files)
    if not files:
        return None
    return sorted(files)[-1]  

def load_dataset(dataset):
    latest_file = get_latest_file(dataset["prefix"])
    if not latest_file:
        print(f"No file found for {dataset['name']}")
        return

    print(f"Loading {latest_file} into table `{dataset['name']}`...")

    if latest_file.endswith(".csv"):
        df = pd.read_csv(latest_file)
    elif latest_file.endswith(".json"):
        df = pd.read_json(latest_file, lines=True) if open(latest_file).read(1) == '{' else pd.read_json(latest_file)
    else:
        print(f"Unsupported file type: {latest_file}")
        return

    df.to_sql(dataset["name"], con=engine, if_exists="replace", index=False)
    print(f"Loaded {len(df)} rows into {dataset['name']}")

if __name__ == "__main__":
    for ds in datasets:
        load_dataset(ds)


