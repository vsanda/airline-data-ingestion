import os
import json
from datetime import datetime

def save_json(data, prefix, name):
    today = datetime.today().strftime("%Y%m%d")
    directory = f"data/raw/{prefix}"
    os.makedirs(directory, exist_ok=True)
    path = f"{directory}/{name}_{today}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[✓] Saved {len(data)} records to {path}")
