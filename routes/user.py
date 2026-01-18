from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from database import user_collection, event_collection
from schemas.user import UserCreate
from utils.time import IST
from utils.validate import verify_access_token
from utils.verify import verify_user_payload, verify_event
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

    if not user_collection.find_one({
        "_id": user_id,
        "registered_event.event_id": event_id
    }):
        
        user_collection.update_one(
            {"_id": user_id},
            {"$push": {"registered_event": {"event_id": event_id,"registered_on": timestamp, "team":None}}}
        )


    if not event_collection.find_one({
        "_id": event_id,
        "registered_user.user_id": user_id
    }):
        
        event_collection.update_one(
            {"_id": event_id},
            {"$push": {"registered_user": {"user_id": user_id,"registered_on": timestamp, "team":None}}}
        )


    return {"message": "Event registered successfully"}

