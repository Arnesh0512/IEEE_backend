from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from database import user_collection, event_collection
from schemas.user import UserCreate
from bson import ObjectId
from utils.time import IST

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/signup")
def signup_user(user: UserCreate):
    

    user_data = user.model_dump(mode="json")
    #user_data["registered_event"] = [ObjectId(event_id) for event_id in user.registered_event]


    user_collection.insert_one(user_data)
    return {"message": "User registered successfully"}





@router.post("/register-event")
def register_event(event_id: str, user_id: str):

    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(event_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id or event_id"
        )
    
    user_oid = ObjectId(user_id)
    event_oid = ObjectId(event_id)

    if not event_collection.find_one({"_id": event_oid}) or not user_collection.find_one({"_id": user_oid}):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    timestamp = datetime.now(IST).isoformat()

    if not user_collection.find_one({
        "_id": user_oid,
        "registered_event.event_id": event_oid
    }):
        
        registration_data = {
            "event_id": event_oid,
            "registered_on": timestamp
        }
        user_collection.update_one(
            {"_id": user_oid},
            {"$push": {"registered_event": registration_data}}
        )

    if not event_collection.find_one({
        "_id": event_oid,
        "registered_user.user_id": user_oid
    }):
        
        registration_data = {
            "user_id": user_oid,
            "registered_on": timestamp
        }
        event_collection.update_one(
            {"_id": event_oid},
            {"$push": {"registered_user": registration_data}}
        )


    return {"message": "Event registered successfully"}

