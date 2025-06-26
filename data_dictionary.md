# ✈️ Airline Data Dictionary (updated 06-25-25)

## 📍 Airports

| Column         | Type    | Description                              |
|----------------|---------|------------------------------------------|
| airport_code   | TEXT    | 3-letter IATA code (e.g., "JFK")         |
| name           | TEXT    | Full airport name                        |
| city           | TEXT    | City where airport is located            |
| country        | TEXT    | Country where airport is located         |
| timezone       | TEXT    | Timezone string (e.g., "America/New_York") |
| elevation_ft   | INT     | Elevation in feet                        |
| date           | DATE    | Date of record (for slowly changing fields) |

---

## 🛫 Flights (Live/OpenSky or Simulated)

| Column          | Type      | Description                                |
|-----------------|-----------|--------------------------------------------|
| icao24          | TEXT      | Aircraft identifier                        |
| callsign        | TEXT      | Flight callsign                            |
| origin_country  | TEXT      | Country of aircraft origin                 |
| time_position   | FLOAT     | Epoch timestamp when position was recorded |
| last_contact    | FLOAT     | Epoch timestamp of last signal             |
| longitude       | FLOAT     | Longitude                                  |
| latitude        | FLOAT     | Latitude                                   |
| baro_altitude   | FLOAT     | Altitude based on pressure                 |
| on_ground       | BOOLEAN   | Whether the aircraft is on the ground      |
| velocity        | FLOAT     | Speed in m/s                               |
| heading         | FLOAT     | Compass direction                          |
| vertical_rate   | FLOAT     | Rate of ascent/descent                     |
| sensors         | TEXT      | Sensor metadata                            |
| geo_altitude    | FLOAT     | GPS-based altitude                         |
| squawk          | TEXT      | Squawk code                                |
| spi             | BOOLEAN   | Transponder status                         |
| position_source | INT       | Source of position data                    |
| timestamp       | TIMESTAMP | ISO datetime of snapshot                   |
| flight_id       | TEXT      | Synthetic ID for joining                   |
| aircraft_id     | TEXT      | Linked to aircraft inventory               |

---

## 🧑‍✈️ Crew Payroll

| Column             | Type      | Description                              |
|--------------------|-----------|------------------------------------------|
| crew_id            | UUID      | Unique crew identifier                   |
| name               | TEXT      | Crew member's full name                  |
| role               | TEXT      | Role: 'Pilot', 'Co-Pilot', etc.          |
| monthly_salary_usd | FLOAT     | Monthly salary                           |
| hours_logged       | INT       | Total hours logged                       |
| flight_id          | TEXT      | Flight assignment                        |
| flight_day         | DATE      | Day of flight duty                       |
| duty_start         | TIMESTAMP | Start of shift                           |
| duty_end           | TIMESTAMP | End of shift                             |
| recorded_at        | TIMESTAMP | Timestamp when record was captured       |

---

## 🎫 Bookings

| Column             | Type      | Description                              |
|--------------------|-----------|------------------------------------------|
| booking_id         | UUID      | Unique booking ID                        |
| passenger_name     | TEXT      | Full name                                |
| flight_id          | TEXT      | Linked flight ID                         |
| seat_number        | TEXT      | Alphanumeric seat code                   |
| departure_time     | TIMESTAMP | When flight departs                      |
| booking_time       | TIMESTAMP | When booking was made                    |
| booking_status     | TEXT      | 'confirmed', 'cancelled', 'checked_in'   |
| ticket_price_usd   | FLOAT     | Price paid for ticket                    |
| flight_day         | DATE      | Derived from departure_time              |

---

## 🛢️ Fuel Prices (Enriched via Faker + EIA)

| Column               | Type    | Description                                      |
|----------------------|---------|--------------------------------------------------|
| product              | TEXT    | Internal product code (e.g., EIA-WTI)           |
| product_name         | TEXT    | Full product name (e.g., Jet Fuel)              |
| process              | TEXT    | Internal process code                           |
| process_name         | TEXT    | Human-readable name (e.g., 'Spot Price')        |
| region_name          | TEXT    | Region (e.g., Gulf Coast, Midwest)              |
| price_per_gallon_usd | FLOAT   | Simulated retail price per gallon               |
| price_month          | DATE    | Reporting month (e.g., 2024-12)                 |
| fuel_category        | TEXT    | e.g., 'jet_fuel', 'diesel', 'crude_oil'         |
| flight_day           | DATE    | Randomly sampled day to associate with flight ops |

---

## 🛩️ Aircraft Inventory

| Column       | Type    | Description                            |
|--------------|---------|----------------------------------------|
| aircraft_id  | TEXT    | Tail number (e.g., "N85403")           |
| model        | TEXT    | Aircraft model (e.g., A320)            |
| manufacturer | TEXT    | Manufacturer name (e.g., Boeing)       |
| capacity     | INT     | Number of seats                        |
| status       | TEXT    | 'active', 'retired', etc.              |
| date         | DATE    | Snapshot date                          |

---

## 🛠️ Supplier Logs

| Column             | Type    | Description                            |
|--------------------|---------|----------------------------------------|
| supplier           | TEXT    | Supplier company name                  |
| part               | TEXT    | Part type                              |
| order_date         | DATE    | When order was placed                  |
| expected_delivery  | DATE    | When delivery is expected              |
| status             | TEXT    | 'on-time', 'delayed', 'backordered'    |
| delay_days         | INT     | Delay length (if any)                  |
| cost_usd           | FLOAT   | Cost of part                           |
| flight_day         | DATE    | Associated operational day (if any)    |

---