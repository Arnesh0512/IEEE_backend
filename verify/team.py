from fastapi import HTTPException, status
from database import user_collection, team_collection, event_collection
from bson import ObjectId
from typing import Tuple




def verify_teamName(team_name: str, event_id: ObjectId, type:str) -> Tuple[dict|None, str]:
    team_name = team_name.strip().lower()

    team = team_collection.find_one({
        "event_id": event_id,
        "team_name": team_name
    })

    if type=="N":
        if team:
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Team name already taken"
            )
        
    if type=="Y":
        if not team:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such team for this event"
            )
        
    return (team,team_name)




def verify_teamMember(
    team: dict,
    user_id: ObjectId,
    type: str
):
    leader_id = team.get("leader_id")
    members = team.get("members", [])


    if leader_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is team leader"
        )

    is_member = user_id in members

    if type == "N":
        if is_member:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already joined this team"
            )

    if type == "Y":
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not a member of this team"
            )



    





def verify_teamLeader(
    team: dict,
    user_id: ObjectId,
    type: str
):

    leader_id = team.get("leader_id")

    if type == "N":
        if leader_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is team leader"
            )

    elif type == "Y":
        if leader_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not team leader"
            )





def verify_user_not_in_team(
    user: dict,
    event_id: ObjectId
):
    for reg in user.get("registered_event", []):
        if (
            reg.get("event_id") == event_id
            and "team" in reg
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already belongs to a team for this event"
            )




def verify_is_team_allowed(event: dict):
    if not event.get("event_team_allowed", False):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Team registration not allowed"
        )

    

def verify_team_by_id(team_id: str) -> Tuple[dict,ObjectId]:
    if not ObjectId.is_valid(team_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid team_id"
        )
    
    team_oid = ObjectId(team_id)

    team = team_collection.find_one({"_id": team_oid})
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    return (team,team_oid)


def verify_in_team(
    team: dict,
    user_id: ObjectId
):
    leader_id = team.get("leader_id")
    members = team.get("members", [])

    is_leader = leader_id == user_id
    is_member = user_id in members

    if not is_leader and not is_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not in team"
        )

def verify_team_size(
        event: dict,
        team:dict
):
    team_size = event["event_team_size"]-1

    member_size = len(team["members"])

    if team_size == member_size:
        raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Team has reached max capacity"
            )
