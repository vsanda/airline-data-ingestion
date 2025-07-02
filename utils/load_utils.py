import os
import pandas as pd
from sqlalchemy import text
import glob
import json

def get_latest_file(prefix, name):
    pattern_csv = f"data/raw/{prefix}/{name}_*.csv"
    pattern_json = f"data/raw/{prefix}/{name}_*.json"
    files = glob.glob(pattern_csv) + glob.glob(pattern_json)
    if not files:
        return None
    return sorted(files)[-1]

def load_to_postgres(filepath, table_name, engine, schema='public'):
    if filepath.endswith(".csv"):
        df = pd.read_csv(filepath)
    elif filepath.endswith(".json"):
        df = pd.read_json(filepath, lines=True) if open(filepath).read(1) == '{' else pd.read_json(filepath)
    else:
        raise ValueError(f"Unsupported file type: {filepath}")
    
    fq_table = f"{schema}.{table_name}" if schema else table_name
    print(f"DROP TABLE IF EXISTS {fq_table} CASCADE")
    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {fq_table} CASCADE"))

    df.to_sql(table_name, con=engine, if_exists="replace", index=False)
    print(f"Loaded {len(df)} rows into {table_name}")

def load_and_insert_all_files(prefix, table_name, engine, chunk_size=5000):
    pattern = f"data/raw/{prefix}/{table_name}_*.csv"
    files = sorted(glob.glob(pattern))  # sort for determinism

    for file_path in files:
        print(f"Inserting: {file_path}")
        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            chunk.to_sql(table_name, con=engine, if_exists='append', index=False)

def load_dim_flights(directory="data/static/dim_flights", days_back=None):
    files = sorted(glob.glob(f"{directory}/dim_flights_*.json"))

    if days_back:
        files = files[-days_back:]

    flights = []
    for file in files:
        with open(file, "r") as f:
            day_flights = json.load(f)
            flights.extend(day_flights)

    return flights
