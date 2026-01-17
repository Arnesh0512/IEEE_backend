from fastapi import APIRouter, HTTPException
from datetime import datetime, date
from database import user_collection
from utils.time import IST
from utils.validate import verify_google_token,create_access_token


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/user")
def google_auth(data: dict):
    
    token = data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token missing")

    idinfo = verify_google_token(token)
    email = idinfo["email"]

    user = user_collection.find_one({"email": email})
    if user:
        user_id = str(user["_id"])
    else:
        result = user_collection.insert_one({
            "email": email,
            "created_on": datetime.now(IST).isoformat(),
            "registered_event": []
        })
        user_id = str(result.inserted_id)


    today=date.today()
    payload = {
        "user_id":user_id,
        "email": email,
        "exp": datetime(today.year + (1 if today.month > 6 else 0),6,30, 18,30)
    }
    
    access_token = create_access_token(payload)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }