import os
import json
from datetime import datetime
import pandas as pd

def save_json(data, prefix, name):
    today = datetime.today().strftime("%Y%m%d")
    directory = f"data/raw/{prefix}"
    os.makedirs(directory, exist_ok=True)
    path = f"{directory}/{name}_{today}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[✓] Saved {len(data)} records to {path}")

def save_csv(data, prefix, name):
    today = datetime.today().strftime("%Y%m%d")
    directory = f"data/raw/{prefix}"
    os.makedirs(directory, exist_ok=True)
    path = f"{directory}/{name}_{today}.csv"

    if isinstance(data, list):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        raise ValueError("Data must be a list of dicts or a pandas DataFrame")

    df.to_csv(path, index=False)
    print(f"[✓] Saved {len(df)} records to {path}")