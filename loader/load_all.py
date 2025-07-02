from load_bookings import load_bookings
from load_crew_payroll import load_crew_payroll
from load_flights import load_flights
from load_fuel import load_fuel
from load_inventory import load_inventory
from load_suppliers import load_suppliers

if __name__ == "__main__":
    load_bookings()
    load_crew_payroll()
    load_flights()
    load_fuel()
    load_inventory()
    load_suppliers()
    print("all raw data are saved to postgres successfully!")
