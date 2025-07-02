import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine
from data.static.dim_routes import dim_routes
from data.static.dim_aircraft import dim_aircraft
from data.static.dim_crew import dim_crew
from data.static.dim_suppliers import dim_suppliers
from utils.load_utils import get_latest_file, load_to_postgres, load_and_insert_all_files

load_dotenv()
engine = create_engine(os.getenv("POSTGRES_URL"))

# define the dim tables
dim_routes = pd.DataFrame(dim_routes)
dim_aircraft = pd.DataFrame(dim_aircraft)
dim_crew = pd.DataFrame(dim_crew)
dim_suppliers = pd.DataFrame(dim_suppliers)

dim_tables = {
    "dim_aircraft": dim_aircraft,
    "dim_routes": dim_routes,
    "dim_suppliers": dim_suppliers,
    "dim_crew_members": dim_crew,
}

for table_name, df in dim_tables.items():
    print(f"Loading {table_name}...")
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",  # Use "replace" if doing full reload
        index=False,
        method="multi",
    )

print("All dim_* tables loaded successfully.")

# if __name__ == "__main__":
#     main()
