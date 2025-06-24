# ✈️ Data Ingestion Module – Airline Supply Chain Project

This module handles ingestion of raw operational data for a simulated airline supply chain analytics pipeline. The focus is on integrating multiple data sources into a unified data lake (or staging layer) for downstream processing.

## Ingested Datasets

| Dataset           | Source Type         | Description                                                                |
|------------------|---------------------|-----------------------------------------------------------------------------|
| `flights.csv`     | Simulated / CSV     | Historical flight-level data (carrier, delay, distance, etc.)              |
| `fuel_prices.csv` | API (EIA) + Faker   | Monthly jet fuel and crude oil spot prices by region                       |
| `supplier_logs.csv` | Simulated / JSON  | Fuel supplier delivery and refill events (used for SLA/risk tracking)      |

## Features

- Fetches public fuel price data via the [EIA API](https://api.eia.gov/)
- Falls back to synthetic values using `Faker` when the API lacks granularity
- Saves all raw outputs as flat files to `data/raw/`
- Future-ready for orchestration via Airflow pipelines

## Folder Structure

```
airline-data-ingestion/
├── ingest/
│   ├── fetch_fuel_prices.py
│   ├── fetch_flight_data.py
│   ├── fetch_supplier_logs.py
│
├── data/
│   └── raw/
│       ├── fuel_prices.csv
│       ├── flights.csv
│       └── supplier_logs.csv
```

## Usage

Run each ingestion script individually to populate the raw data layer:

```bash
python ingest/fetch_fuel_prices.py
python ingest/fetch_flight_data.py
python ingest/fetch_supplier_logs.py
```

All output files are written to `data/raw/`.

## External APIs Used

- **EIA (U.S. Energy Information Administration)**  
  **Endpoint**: `https://api.eia.gov/v2/petroleum/pri/rac2/data/`  
  **Use**: Retrieves monthly jet fuel and crude oil spot prices by region.  
  **Fallback**: If price values are missing or unavailable, realistic data is generated using `Faker`.

- **OpenSky Network API**  
  **Use**: Intended for fetching historical or real-time flight-level data.  
  **Note**: Used for flight simulation, but may be supplemented or replaced with static files depending on rate limits or availability.

- **Faker**  
  **Use**: Simulates synthetic logs for supplier fuel deliveries and SLA events.  
  **Note**: Used exclusively for generating supplier operational events (JSON format).

## Notes

- Jet fuel price data may not always contain price values directly in the EIA response. This module includes graceful degradation logic using Faker to simulate realistic fallback data.
- All ingested data is designed for learning/demo purposes — not for production or financial use.
- This module can be integrated into an Airflow DAG or used as a standalone pre-processing stage for analytics modeling.
---
