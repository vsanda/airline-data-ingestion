import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from sqlalchemy import create_engine
from utils.load_utils import get_latest_file, load_to_postgres

load_dotenv()
engine = create_engine(os.getenv("POSTGRES_URL"))

def main():
    prefix = "airports"
    name = "airports_data"
    filepath = get_latest_file(prefix, name)
    if not filepath:
        print(f"No file found for {name}")
        return
    print(f"Loading {filepath}...")
    load_to_postgres(filepath, name, engine)

if __name__ == "__main__":
    main()
