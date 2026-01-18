from fastapi import APIRouter, Depends
from datetime import datetime
from database import team_collection, user_collection, event_collection
from utils.time import IST
from utils.validate import verify_access_token
from utils.verify import verify_user_payload, verify_event, verify_eventRegistry
from utils.verify import  verify_teamName , verify_teamMember, verify_teamLeader
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId

security = HTTPBearer()

router = APIRouter(prefix="/team", tags=["Teams"])




def set_user_team(user_id: ObjectId, event_id: ObjectId, team_id: ObjectId | None):
    user_collection.update_one(
        {"_id": user_id,
        "registered_event.event_id": event_id},
        {"$set": {"registered_event.$.team": team_id}}
    )

    event_collection.update_one(
        {"_id": event_id,
        "registered_user.user_id": user_id},
        {"$set": {"registered_user.$.team": team_id}}
    )




@router.post("/register")
def signup_team(
    event_id: str,
    team_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
    ):

    token = credentials.credentials
    payload = verify_access_token(token)
    user_id ,user_email = verify_user_payload(payload)
    event_id = verify_event(event_id)
    verify_eventRegistry(event_id, user_id)

    team_name = verify_teamName(team_name, event_id, "N")


    team_data={
        "leader_id": user_id,
        "event_id": event_id,
        "team_name": team_name,
        "members":[],
        "registered_on":datetime.now(IST).isoformat()
    }

    team=team_collection.insert_one(team_data)
    team_id = team["_id"]

    set_user_team(user_id, event_id, team_id)


    return {"message": "Team registered successfully"}




@router.patch("/join")
def register_event(
    event_id: str,
    team_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
    token = credentials.credentials
    payload = verify_access_token(token)
    user_id , email = verify_user_payload(payload)
    event_id = verify_event(event_id)
    verify_eventRegistry(event_id, user_id)

    team_name = verify_teamName(team_name, event_id, "Y")
    team = verify_teamMember(team_name, event_id, user_id, "N")
    team_id = team["_id"]

    team_collection.update_one(
        {"_id":team_id},
        {"$push":{
            "members": user_id
        }}
    )
    
    set_user_team(user_id, event_id, team_id)


    return {"message": "Team Member registered successfully"}


@router.delete("/delete")
def delete_team(
    event_id: str,
    team_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    leader_id, email = verify_user_payload(payload)
    event_id = verify_event(event_id)
    verify_eventRegistry(event_id, leader_id)

    team_name = verify_teamName(team_name, event_id, "Y")
    team = verify_teamLeader(team_name, event_id, leader_id, "Y")
    team_id = team["_id"]


    set_user_team(leader_id, event_id, None)
    for member_id in team["members"]:
        set_user_team(member_id, event_id, None)


    team_collection.delete_one({"_id": team_id})

    return {"message": "Team deleted successfully"}


@router.patch("/leave")
def leave_team(
    event_id: str,
    team_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    user_id, _ = verify_user_payload(payload)
    event_id = verify_event(event_id)
    verify_eventRegistry(event_id, user_id)


    team_name = verify_teamName(team_name, event_id, "Y")
    team = verify_teamMember(team_name, event_id, user_id, "Y")
    team_id = team["_id"]


    team_collection.update_one(
        {"_id": team_id},
        {"$pull": {"members": user_id}}
    )
    set_user_team(user_id, event_id, None)

    return {"message": "Left team successfully"}



















