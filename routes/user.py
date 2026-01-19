from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from database import user_collection, event_collection
from schemas.user import UserCreate
from utils.time import IST
from verify.token import verify_access_token
from verify.user import verify_user_payload
from verify.event import verify_event, verify_eventRegistry
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
            "registered_event":0
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

    event = event_collection.find_one(
        
    )