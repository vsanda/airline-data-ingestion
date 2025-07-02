from fetch_flight_data import fetch_flight_data
from fetch_fuel_prices import fetch_fuel_prices
from generate_bookings import generate_bookings
from generate_crew_payroll import generate_payroll
from generate_plane_inventory import generate_aircraft
from generate_supplier_logs import generate_supply_orders

if __name__ == "__main__":
    fetch_flight_data()
    fetch_fuel_prices()
    generate_bookings()
    generate_payroll()
    generate_aircraft()
    generate_supply_orders()
    print("all ingest files generated successfully!")
