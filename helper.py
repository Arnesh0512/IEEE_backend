from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from utils.reader import uri
from datetime import datetime, timezone, timedelta

# IST timezone
IST = timezone(timedelta(hours=5, minutes=30))

client = MongoClient(uri, server_api=ServerApi("1"))

db = client["2026_2027"]     # change DB name if needed
event_col = db["event"]

created_time = datetime.now(IST).isoformat()
updated_events = 0

for event in event_col.find({"created_on": {"$exists": False}}):
    event_col.update_one(
        {"_id": event["_id"]},
        {"$set": {"created_on": created_time}}
    )
    updated_events += 1

print(f"Added created_on to {updated_events} event documents.")
