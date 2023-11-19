from faker import Faker
import json
import random

fake = Faker()

data = []

for _ in range(100000000):
    item = {
        "level": random.choice(["error", "info", "warning", "debug"]),
        "message": fake.sentence(),
        "resourceId": f"server-{fake.random_number(digits=4)}",
        "timestamp": fake.date_time_this_decade().isoformat(),
        "traceId": fake.uuid4(),
        "spanId": f"span-{fake.random_number(digits=3)}",
        "commit": fake.sha1(),
        "metadata": {
            "parentResourceId": f"server-{fake.random_number(digits=4)}"
        }
    }
    data.append(item)

with open('data.json', 'w') as f:
    json.dump(data, f, indent=2)