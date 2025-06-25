from faker import Faker
import random
from datetime import datetime, timedelta
from utils.save_utils import save_json

fake = Faker()

def generate_and_save(n=50):
    data = []
    for _ in range(n):
        flight_time = fake.date_time_between(start_date='-30d', end_date='+30d')
        data.append({
            "booking_id": fake.uuid4(),
            "passenger_name": fake.name(),
            "flight_id": fake.bothify("FL####"),
            "seat_number": fake.bothify("##?"),
            "departure_time": flight_time.isoformat(),
            "booking_time": (flight_time - timedelta(days=random.randint(1, 30))).isoformat(),
            "status": random.choice(["confirmed", "cancelled", "checked_in"]),
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        })
    save_json(data, prefix="bookings", name="passenger_data")

if __name__ == "__main__":
    generate_and_save()
