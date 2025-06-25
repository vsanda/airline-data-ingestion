import pandas as pd
from faker import Faker
from random import choice, randint
from pathlib import Path
from datetime import datetime

fake = Faker()

def simulate_supplier_logs(num_rows=25):
    print("simulating supplier logs...")

    parts = ["hydraulic pump", "landing gear", "avionics unit", "turbine blade", "oxygen valve"]
    statuses = ["on-time", "delayed", "lost", "backordered"]

    data = []
    for i in range(num_rows):
        row = {
            "supplier": fake.company(),
            "part": choice(parts),
            "order_date": fake.date_between(start_date='-30d', end_date='today'),
            "expected_delivery": fake.date_between(start_date='today', end_date='+15d'),
            "status": choice(statuses),
            "delay_days": randint(0, 10) if choice([True, False]) else 0
        }
        data.append(row)

    df = pd.DataFrame(data)
    print(df.head())

    today = datetime.utcnow().strftime("%Y-%m-%d")
    output_path = Path(f"data/raw/suppliers/supplier_logs_{today}.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Supplier logs saved to {output_path}")

if __name__ == "__main__":
    simulate_supplier_logs()
