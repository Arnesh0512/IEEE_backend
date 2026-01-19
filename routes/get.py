from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from verify.token import verify_access_token
from verify.sudo import verify_sudo_payload
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
    user_collection = db["users"]

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
