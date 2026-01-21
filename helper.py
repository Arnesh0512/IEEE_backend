from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from utils.reader import uri
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

client = MongoClient(uri, server_api=ServerApi("1"))

db = client["2026_2027"]   # target academic DB
user_col = db["user"]
team_col = db["team"]

# ----------------------------
# PART 1: Update user documents
# team -> team_id
# ----------------------------
updated_users = 0

for user in user_col.find({"registered_event": {"$exists": True}}):
    events = user.get("registered_event", [])
    changed = False

    for event in events:
        if isinstance(event, dict) and "team" in event:
            event["team_id"] = event.pop("team")
            changed = True

    if changed:
        user_col.update_one(
            {"_id": user["_id"]},
            {"$set": {"registered_event": events}}
        )
        updated_users += 1

print(f"Updated {updated_users} user documents (team → team_id).")

# ----------------------------
# PART 2: Lowercase team_name
# ----------------------------
updated_teams = 0

for team in team_col.find({"team_name": {"$exists": True}}):
    team_name = team.get("team_name")

    if isinstance(team_name, str):
        lower_name = team_name.lower()

        if team_name != lower_name:
            team_col.update_one(
                {"_id": team["_id"]},
                {"$set": {"team_name": lower_name}}
            )
            updated_teams += 1

print(f"Updated {updated_teams} team documents (lowercased team_name).")

# ----------------------------
# PART 3: Add created_on (IST)
# ----------------------------
created_users = 0
created_time = datetime.now(IST).isoformat()

for user in user_col.find({"created_on": {"$exists": False}}):
    user_col.update_one(
        {"_id": user["_id"]},
        {"$set": {"created_on": created_time}}
    )
    created_users += 1

print(f"Added created_on to {created_users} user documents.")
