from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from database import user_collection, event_collection, team_collection
from schemas.user import UserCreate
from utils.time import IST
from verify.token import verify_access_token
from verify.user import verify_user_payload
from verify.event import verify_event, verify_eventRegistry
from verify.team import verify_team_by_id, verify_in_team
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

router = APIRouter(prefix="/users", tags=["Users"])




@router.patch("/register")
def signup_user(
    user: UserCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
    ):

    token = credentials.credentials
    payload = verify_access_token(token)
    user_id ,email = verify_user_payload(payload)
    
    
    update_data = user.model_dump(mode="json")
    update_data["registered_event"] = []

    if email != update_data["email"].lower():
        raise HTTPException(status_code=404, detail="Email Mismatch found")

    user_collection.update_one(
        {"_id": user_id},
        {"$set": update_data}
    )

    return {"message": "User registered successfully"}





@router.patch("/register-event")
def register_event(
    event_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
    token = credentials.credentials
    payload = verify_access_token(token)
    user_id , email = verify_user_payload(payload)
    event_id = verify_event(event_id)

    timestamp = datetime.now(IST).isoformat()


    verify_eventRegistry(event_id, user_id, "N")
        
    user_collection.update_one(
        {"_id": user_id},
        {"$push": {"registered_event": {"event_id": event_id,"registered_on": timestamp}}}
    )
        
    event_collection.update_one(
        {"_id": event_id},
        {"$push": {"registered_user": user_id}}
    )


    return {"message": "Event registered successfully"}



@router.get("/profile")
def get_user_details(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_access_token(token)
    user_id ,email = verify_user_payload(payload)

    user = user_collection.find_one(
        {"_id": user_id, "email": email},
        {
            "_id": 0,
            "registered_event":0,
            "remark":0
        }
    )

    return {
        "success": True,
        "data": user
    }


@router.get("/registered")
def get_registered_events_teams(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_access_token(token)
    user_id ,email = verify_user_payload(payload)

    user = user_collection.find_one(
        {"_id": user_id, "email": email},
        {
            "_id": 0,
            "registered_event":1
        }
    )

    event = event_collection.find(
        {},
        {"_id":1,
         "event_name":1})
    
    team = team_collection.find(
        {},
        {"_id":1,
         "team_name":1,
         "registered_on":1})
    
    event_map = {
        str(e["_id"]): e["event_name"]
        for e in event
    }

    team_map = {
        str(t["_id"]): {
            "team_name": t["team_name"],
            "team_created_on": t.get("registered_on")
        }
        for t in team
    }

    result = []

    for reg in user.get("registered_event", []):
        event_id = str(reg["event_id"])
        team_id = str(reg.get("team_id")) if reg.get("team_id") else None

        result.append({
            "event_id": event_id,
            "event_name": event_map.get(event_id),
            "registered_for_event_on": reg.get("registered_on"),
            "team_id": team_id,
            "team_name": team_map.get(team_id, {}).get("team_name"),
            "team_created_on": team_map.get(team_id, {}).get("team_created_on")
        })

    return {"registered_event": result}

    
@router.get("/event")
def get_registered_event(
    event_id:str,
    credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_access_token(token)
    user_id ,email = verify_user_payload(payload)
    event_id = verify_event(event_id)
    verify_eventRegistry(event_id,user_id)
    
    event = event_collection.find_one(
        {"_id":event_id},
        {
            "_id":0,
            "registered_user":0,
            "registered_team":0,
            "remark":0
        }
    )

    return {
        "success": True,
        "data": event
    }



@router.get("/team")
def get_team(
    team_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    user_id, email = verify_user_payload(payload)
    team_id = verify_team_by_id(team_id)
    verify_in_team(team_id, user_id)


    team = team_collection.find_one(
        {"_id": team_id},
        {"remark": 0}
    )

    event = event_collection.find_one(
        {"_id": team["event_id"]},
        {"event_name": 1}
    )

    leader = user_collection.find_one(
        {"_id": team["leader_id"]},
        {"name": 1, "email": 1}
    )

    members_cursor = user_collection.find(
        {"_id": {"$in": team.get("members", [])}},
        {"name": 1, "email": 1}
    )

    members = [
        {
            "name": member["name"],
            "email": member["email"]
        }
        for member in members_cursor
    ]

    data = {
        "team_name": team["team_name"],
        "event_name": event["event_name"],
        "leader_name": leader["name"],
        "leader_email": leader["email"],
        "team_created_on": team["created_on"],
        "members": members
    }

    return {
        "success": True,
        "data": data
    }


@router.get("/events")
def get_this_session_events(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    user_id, email = verify_user_payload(payload)

    events_cursor = event_collection.find(
        {},
        {
            "registered_user": 0,
            "registered_team": 0,
            "remark": 0
        }
    )

    events = []
    for event in events_cursor:
        event["_id"] = str(event["_id"])
        events.append(event)

    return {
        "success": True,
        "data": events
    }


