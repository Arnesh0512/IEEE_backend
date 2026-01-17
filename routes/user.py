from fastapi import APIRouter, HTTPException, status, Depends, Header
from datetime import datetime
from database import user_collection, event_collection
from schemas.user import UserCreate
from bson import ObjectId
from utils.time import IST
from utils.validate import verify_access_token
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

    user_id = payload.get("user_id")
    email = payload.get("email").lower()
    if not user_id or not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    

    existing_user = user_collection.find_one({
        "_id": ObjectId(user_id),
        "email": email
    })
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    

    update_data = user.model_dump(mode="json")
    update_data["registered_event"] = []

    if email.lower() != update_data["email"].lower():
        raise HTTPException(status_code=404, detail="Email Mismatch found")

    user_collection.update_one(
        {"_id": ObjectId(user_id)},
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
    user_id = payload.get("user_id")
    email = payload.get("email").lower()
    if not user_id or not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")


    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(event_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id or event_id"
        )
    
    user_oid = ObjectId(user_id)
    event_oid = ObjectId(event_id)

    if not event_collection.find_one({"_id": event_oid}) or not user_collection.find_one({"_id": user_oid, "email": email}):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    timestamp = datetime.now(IST).isoformat()

    if not user_collection.find_one({
        "_id": user_oid,
        "registered_event.event_id": event_oid
    }):
        
        user_collection.update_one(
            {"_id": user_oid},
            {"$push": {"registered_event": {"event_id": event_oid,"registered_on": timestamp}}}
        )


    if not event_collection.find_one({
        "_id": event_oid,
        "registered_user.user_id": user_oid
    }):
        
        event_collection.update_one(
            {"_id": event_oid},
            {"$push": {"registered_user": {"user_id": user_oid,"registered_on": timestamp}}}
        )


    return {"message": "Event registered successfully"}

