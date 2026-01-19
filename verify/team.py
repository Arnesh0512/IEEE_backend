from fastapi import HTTPException, status
from database import user_collection, team_collection, event_collection
from bson import ObjectId
from typing import Tuple




def verify_teamName(team_name: str, event_id: ObjectId, type:str) -> Tuple[str,int]:
    team_name = team_name.strip().lower()

    exists = team_collection.find_one({
        "event_id": event_id,
        "team_name": team_name
    })

    if type=="N":
        if exists:
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Team name already taken"
            )
        
    if type=="Y":
        if not exists:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such team for this event"
            )
        
    return team_name
        
def verify_teamMember(team_name: str, event_id: ObjectId, user_id:ObjectId, type:str) -> ObjectId:
    team = team_collection.find_one({
        "event_id": event_id,
        "team_name": team_name
    })

    if team["leader_id"] == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is Leader"
        )

    if type=="N":
        if user_id in team["members"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already joined this team"
            )
    
    if type=="Y":
        if user_id not in team["members"]:
            raise HTTPException(
                status_code=status.HTTP_409_NOT_FOUND,
                detail="User is not a member"
            )
    
    return team

def verify_teamLeader(team_name: str, event_id: ObjectId, user_id:ObjectId, type:str) -> ObjectId:
    team = team_collection.find_one({
        "event_id": event_id,
        "team_name": team_name
    })

    if type=="N":
        if team["leader_id"] == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is team leader"
            )

    if type=="Y":
        if team["leader_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not team leader"
            )

    
    return team

def verify_user_not_in_team(user_id: ObjectId, event_id: ObjectId):
    already_in_team = user_collection.find_one(
        {
            "_id": user_id,
            "registered_event": {
                "$elemMatch": {
                    "event_id": event_id,
                    "team": {"$exists": True}
                }
            }
        }
    )

    if already_in_team:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already belongs to a team for this event"
        )

def verify_is_team_allowed(event_id: ObjectId):
    event = event_collection.find_one({
        "_id":event_id
    })

    if event["event_team_allowed"]==False:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Team registration not allowed"
        )
    

def verify_team_by_id(team_id: str) -> ObjectId:
    if not ObjectId.is_valid(team_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid team_id"
        )
    
    team_oid = ObjectId(team_id)

    if not team_collection.find_one({"_id": team_oid}):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return team_oid


def verify_in_team(team_id: str, user_id:str):
    team=team_collection.find_one({"_id": team_id})
    leader=team["leader_id"] == user_id
    member=user_id in team["members"]

    if not leader or not member:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not in team"
            )


