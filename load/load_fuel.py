import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from utils.load_utils import get_latest_file, load_to_postgres

load_dotenv()
engine = create_engine(os.getenv("POSTGRES_URL"))

def main():
    prefix = "fuel"
    name = "crude_oil_prices"
    filepath = get_latest_file(prefix, name)
    if not filepath:
        print(f"No file found for {name}")
        return
    print(f"Loading {filepath}...")
    load_to_postgres(filepath, name, engine)

if __name__ == "__main__":
    main()
