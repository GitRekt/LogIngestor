import json
import random
from faker import Faker

fake = Faker()

with open('data.json', 'w') as f:
    for _ in range(100000000):
        item = {
            "level": random.choice(["error", "info", "warning", "debug"]),
            "message": fake.sentence(),
            "resourceId": f"server-{fake.random_number(digits=4)}",
            "timestamp": fake.date_time_this_decade().isoformat(),
            "traceId": fake.uuid4(),
            "spanId": f"span-{fake.random_number(digits=3)}",
            "commit": fake.sha1(),
            "metadata": {"parentResourceId": f"server-{fake.random_number(digits=4)}"}
        }
        f.write(json.dumps(item, indent=2) + ',\n')
    f.write("\n]")
    f.seek(0)
    f.write("[\n")