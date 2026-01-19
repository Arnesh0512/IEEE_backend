from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from verify.token import verify_access_token
from verify.sudo import verify_sudo_payload
from verify.user import verify_user_by_id
from utils.pattern import verify_session_db
from database import client

security = HTTPBearer()
router = APIRouter(prefix="/get", tags=["Get"])

@router.get("/{year}/users")
def get_all_users_of_year(
    year: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)

    year = verify_session_db(year)
    db = client[year]
    user_collection = db["user"]

    users_cursor = user_collection.find(
        {},
        {
            "name": 1,
            "email": 1,
            "registered_event": 1
        }
    )

    users = []

    for user in users_cursor:
        registered_events = user.get("registered_event", [])

        no_of_events = len(registered_events)

        no_of_teams = sum(
            1 for e in registered_events if e.get("team") is not None
        )

        no_of_remarks = sum(
            1 for e in registered_events if "remark" in e
        )

        users.append({
            "user_id": str(user["_id"]),
            "name": user.get("name"),
            "email": user.get("email"),
            "no_of_events": no_of_events,
            "no_of_teams": no_of_teams,
            "no_of_remarks": no_of_remarks
        })

    return {
        "success": True,
        "year": year,
        "count": len(users),
        "data": users
    }




@router.get("/{year}/users/{user_id}")
def get_user_details(
    year: str,
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)

    user, user_id, user_email = verify_user_by_id(user_id, "Y")

    year = verify_session_db(year)
    db = client[year]

    event_collection = db["event"]
    team_collection = db["team"]

    event_map = {
        e["_id"]: e.get("event_name")
        for e in event_collection.find(
            {},
            {"_id": 1, "event_name": 1}
        )
    }

    team_map = {
        t["_id"]: t
        for t in team_collection.find(
            {},
            {
                "_id": 1,
                "team_name": 1,
                "leader_id": 1,
                "members": 1
            }
        )
    }

    enriched_registered_events = []

    for reg in user.get("registered_event", []):
        event_id = reg.get("event_id")
        team_id = reg.get("team")
        remark = reg.get("remark")
        registered_on = reg.get("registered_on")

        event_name = event_map.get(event_id)
        team_name = None
        role = None

        if team_id and team_id in team_map:
            team = team_map[team_id]
            team_name = team.get("team_name")

            if team.get("leader_id") == user_id:
                role = "leader"
            elif user_id in team.get("members", []):
                role = "member"

        enriched_registered_events.append({
            "event_id": str(event_id) if event_id else None,
            "event_name": event_name,
            "registered_for_event": registered_on,
            "remark": remark,
            "team_id": str(team_id) if team_id else None,
            "team_name": team_name,
            "role": role
        })

    return {
        "success": True,
        "year": year,
        "user_details": {
            "user_id": str(user_id),
            "email": user_email,
            "registered_event": enriched_registered_events
        }
    }
