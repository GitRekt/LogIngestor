import json
import random
from faker import Faker

fake = Faker()
limit=100
with open('data.json', 'w') as f:
    for i in range(limit):
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
        if(i!=limit-1):
            f.write(json.dumps(item, indent=2) + ',\n')
        else:
            f.write(json.dumps(item, indent=2) + '\n')
    f.write("]")
    f.seek(0)
    f.write("[{\n")