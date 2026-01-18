from fastapi import HTTPException, status
from database import superadmin_collection, admin_collection, user_collection, event_collection, team_collection
from bson import ObjectId
from bson.errors import InvalidId
from typing import Tuple



def verify_user_payload(payload: dict) -> Tuple[ObjectId, str]:

    user_id = payload.get("user_id")
    email = payload.get("email")
    role = payload.get("role")

    if not user_id or not email or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    if role != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a user"
        )
    
    return verify_user(user_id, email)

def verify_user(user_id: str, email: str) -> Tuple[ObjectId, str]:

    email = email.lower()

    try:
        user_obj_id = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id"
        )

    exists = user_collection.find_one({
        "_id": user_obj_id,
        "email": email
    })

    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return (user_obj_id,email)



def verify_admin_payload(payload: dict) -> Tuple[ObjectId, str]:

    admin_id = payload.get("admin_id")
    email = payload.get("email")
    role = payload.get("role")

    if not admin_id or not email or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient privileges"
        )
    
    return verify_admin(admin_id, email)

def verify_admin(admin_id: str, email: str) -> Tuple[ObjectId, str]:
    email = email.lower()

    try:
        admin_obj_id = ObjectId(admin_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin id"
        )

    exists = admin_collection.find_one({
        "_id": admin_obj_id,
        "email": email
    })

    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )

    return (admin_obj_id,email)



def verify_superadmin_payload(payload: dict) -> Tuple[ObjectId, str]:

    super_id = payload.get("superadmin_id")
    email = payload.get("email")
    role = payload.get("role")

    if not super_id or not email or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    if role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient privileges"
        )
    
    return verify_superadmin(super_id, email)

def verify_superadmin(super_id: str, email: str) -> Tuple[ObjectId, str]:
    email = email.lower()

    try:
        super_obj_id = ObjectId(super_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid superadmin id"
        )

    exists = superadmin_collection.find_one({
        "_id": super_obj_id,
        "email": email
    })

    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SuperAdmin not found"
        )

    return (super_obj_id,email)


def verify_event(event_id: str) -> ObjectId:
    if not ObjectId.is_valid(event_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event_id"
        )
    
    event_oid = ObjectId(event_id)

    if not event_collection.find_one({"_id": event_oid}):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return event_oid



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




def verify_eventRegistry(event_id: ObjectId, user_id:ObjectId) -> bool:
    
    user_check = user_collection.find_one({
        "_id": user_id,
        "registered_event": {
            "$elemMatch": {
                "event_id": event_id,
                "team": None
            }
        }
    })

    event_check = event_collection.find_one({
        "_id": event_id,
        "registered_user": {
            "$elemMatch": {
                "user_id": user_id,
                "team": None
            }
        }
    })

    if not user_check or event_check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not registered for this event or already in a team"
        )
    
    return True


