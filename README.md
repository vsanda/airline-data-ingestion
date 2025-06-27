# ✈️ Data Ingestion Module – Airline Supply Chain Project

This module handles ingestion of raw operational data for a simulated airline supply chain analytics pipeline. It integrates both real and synthetic data sources into a PostgreSQL staging layer for downstream transformation and basic P/L modeling (via dbt, Airflow, Apache superset, etc).

## Ingested Datasets

| Dataset             | Source Type         | Frequency   | Description |
|---------------------|---------------------|-------------|-------------|
| `flights`           | OpenSky / Simulated | Daily       | Historical flight-level data (carrier, delay, distance, etc.) |
| `crude_oil_prices`  | EIA API + Faker     | Daily       | Jet fuel and crude oil spot prices by region                  |
| `supplier_logs`     | Simulated / JSON    | Daily       | Fuel supplier delivery and refill events for SLA tracking     |
| `plane_inventory`   | Simulated / Faker   | Weekly      | Aircraft metadata: model, capacity, maintenance flags         |
| `passenger_bookings`| Simulated / Faker   | Daily       | Ticket-level booking data: route, price, passenger ID         |
| `crew_payroll`      | Simulated / Faker   | Monthly     | Salaries, hours flown, bonuses, and crew role data            |
| `airports_metadata` | Public JSON / Faker | Quarterly   | Airport codes, cities, timezones, and regions                 |

## Features

- Modular ingestion scripts for each dataset
- Supports CSV + JSON file formats
- Graceful fallback to Faker if external APIs are unavailable
- Raw output saved under `data/raw/` with dates
- Keys saved under `data/keys/` for joined logic
- PostgreSQL used as the staging target
- Future-ready for orchestration via Airflow

## Folder Structure

```
airline-data-ingestion/
├── ingest/
│   ├── fetch_*.py                # Raw data generation scripts using APIs
│   ├── generate_*.py             # Raw data generation scripts
│
├── loader/
│   ├── load_fuel.py
│   ├── load_flights.py
│   ├── load_suppliers.py
│   ├── load_planes.py
│   ├── load_passengers.py
│   ├── load_payroll.py
│   └── load_airports.py
│
├── utils/                      # Shared functions
│   ├── load_utils.py            
│   ├── save_utils.py            
│
├── data/
│   └── raw/
│       ├── fuel/
│       ├── flights/
│       ├── suppliers/
│       ├── planes/
│       ├── passengers/
│       ├── payroll/
│       └── airports/
```

## Usage

### Ingest raw files:

```bash
python ingest/fetch_fuel_prices.py
python ingest/fetch_flight_data.py
python ingest/fetch_supplier_logs.py
# ...plus any synthetic generators for planes, passengers, payroll, airports
```

### Load latest file to PostgreSQL:

```bash
python loader/load_fuel.py
python loader/load_flights.py
python loader/load_suppliers.py
python loader/load_planes.py
python loader/load_passengers.py
python loader/load_payroll.py
python loader/load_airports.py
```

All tables will be created (or replaced) in the target PostgreSQL database specified in `.env`.

## 🌐 External APIs Used

### 🔌 EIA – U.S. Energy Information Administration

- **Endpoint:** https://api.eia.gov/v2/petroleum/pri/rac2/data/
- **Purpose:** Jet fuel & crude oil price data by region
- **Fallback:** Uses Faker for synthetic prices when API fails or lacks data

### ✈️ OpenSky Network API

- **Purpose:** Flight movement simulation (optional, rate-limited)
- **Fallback:** Static flight data or Faker-based generator for simulation

### 🧪 Faker (Python)

- **Purpose:** Simulates synthetic datasets: suppliers, planes, bookings, payroll, airports

## 📝 Notes

- All data is intended for educational/demo use — not suitable for production or financial reporting.
- The ingestion system is modular and DAG-friendly. Easily plug each loader script into an Airflow DAG with custom schedules.
- Dates in filenames support partitioning and time-based loading in future transformations.
