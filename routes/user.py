from fastapi import APIRouter, HTTPException
from datetime import datetime
from database import user_collection
from schemas.user import UserCreate
from utils.time import IST

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register")
def register_user(user: UserCreate):
    if user_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="User already exists")

    user_data = user.model_dump(mode="json")
    user_data["created_on"] = datetime.now(IST).isoformat()
    #user_data["registered_event"] = [ObjectId(event_id) for event_id in user.registered_event]


    user_collection.insert_one(user_data)
    return {"message": "User registered successfully"}
