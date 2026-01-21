from fastapi import APIRouter, Depends
from datetime import datetime
from database import current_team_collection, current_user_collection, current_event_collection
from utils.time import IST
from verify.token import verify_access_token
from verify.user import verify_user_payload
from verify.event import verify_event, verify_eventRegistry
from verify.team import  verify_teamName , verify_teamMember, verify_teamLeader, verify_user_not_in_team, verify_is_team_allowed, verify_team_size
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId

security = HTTPBearer()

router = APIRouter(prefix="/team", tags=["Teams"])




def set_user_team(
    user_id: ObjectId,
    event_id: ObjectId,
    team_id: ObjectId | None
):
    if team_id is None:
        update = {"$unset": {"registered_event.$.team_id": ""}}
    else:
        update = {"$set": {"registered_event.$.team_id": team_id}}

    user_collection = current_user_collection()
    user_collection.update_one(
        {"_id": user_id, "registered_event.event_id": event_id},
        update
    )





@router.post("/register")
def signup_team(
    event_id: str,
    team_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
    ):

    token = credentials.credentials
    payload = verify_access_token(token)
    user, user_id ,user_email = verify_user_payload(payload)
    event, event_id = verify_event(event_id)
    verify_is_team_allowed(event)
    verify_eventRegistry(event_id, user_id, "Y", user, event)

    verify_user_not_in_team(user, event_id)
    team_, team_name = verify_teamName(team_name, event_id, "N")


    team_data={
        "leader_id": user_id,
        "event_id": event_id,
        "team_name": team_name,
        "members":[],
        "registered_on":datetime.now(IST).isoformat()
    }

    team_collection = current_team_collection()
    team=team_collection.insert_one(team_data)
    team_id = team.inserted_id


    event_collection = current_event_collection()
    set_user_team(user_id, event_id, team_id)
    event_collection.update_one(
        {"_id": event_id},
        {"$push": {"registered_team":team_id}}
    )


    return {"message": "Team registered successfully"}




@router.patch("/join")
def register_event(
    event_id: str,
    team_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
    token = credentials.credentials
    payload = verify_access_token(token)
    user, user_id , email = verify_user_payload(payload)
    event, event_id = verify_event(event_id)
    verify_is_team_allowed(event)
    verify_eventRegistry(event_id, user_id, "Y", user, event)
    verify_user_not_in_team(user, event_id)

    team,team_name = verify_teamName(team_name, event_id, "Y")
    verify_team_size(event,team)
    verify_teamMember(team, user_id, "N")
    team_id = team["_id"]

    team_collection = current_team_collection()
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
    leader, leader_id, email = verify_user_payload(payload)
    event, event_id = verify_event(event_id)
    verify_is_team_allowed(event)
    verify_eventRegistry(event_id, leader_id, "Y", leader, event)

    team,team_name = verify_teamName(team_name, event_id, "Y")
    verify_teamLeader(team, leader_id, "Y")
    team_id = team["_id"]


    set_user_team(leader_id, event_id, None)
    for member_id in team["members"]:
        set_user_team(member_id, event_id, None)

    team_collection = current_team_collection()
    team_collection.delete_one({"_id": team_id})

    event_collection = current_event_collection()
    event_collection.update_one(
        {"_id": event_id},
        {"$pull": {"registered_team":team_id}}
    )

    return {"message": "Team deleted successfully"}


@router.patch("/leave")
def leave_team(
    event_id: str,
    team_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    user, user_id, _ = verify_user_payload(payload)
    event, event_id = verify_event(event_id)
    verify_is_team_allowed(event)
    verify_eventRegistry(event_id, user_id, "Y", user, event)


    team, team_name = verify_teamName(team_name, event_id, "Y")
    verify_teamMember(team, user_id, "Y")
    team_id = team["_id"]

    team_collection = current_team_collection()
    team_collection.update_one(
        {"_id": team_id},
        {"$pull": {"members": user_id}}
    )
    set_user_team(user_id, event_id, None)

    return {"message": "Left team successfully"}



















