import os
import pandas as pd
import glob

def get_latest_file(prefix, name):
    pattern_csv = f"data/raw/{prefix}/{name}_*.csv"
    pattern_json = f"data/raw/{prefix}/{name}_*.json"
    files = glob.glob(pattern_csv) + glob.glob(pattern_json)
    if not files:
        return None
    return sorted(files)[-1]

def load_to_postgres(filepath, table_name, engine):
    if filepath.endswith(".csv"):
        df = pd.read_csv(filepath)
    elif filepath.endswith(".json"):
        df = pd.read_json(filepath, lines=True) if open(filepath).read(1) == '{' else pd.read_json(filepath)
    else:
        raise ValueError(f"Unsupported file type: {filepath}")
    
    df.to_sql(table_name, con=engine, if_exists="replace", index=False)
    print(f"Loaded {len(df)} rows into {table_name}")
