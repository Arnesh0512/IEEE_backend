from fastapi import APIRouter
from datetime import datetime, date
from database import current_user_collection
from utils.time import IST
from verify.token import verify_google_token,create_access_token
from verify.admin import verify_admin_by_email
from verify.superadmin import verify_superadmin_by_email

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/user")
def google_auth_user(data: dict):

    idinfo = verify_google_token(data)
    email = idinfo["email"].lower()

    user_collection = current_user_collection()
    user = user_collection.find_one({"email": email})
    if user:
        user_id = str(user["_id"])
    else:
        result = user_collection.insert_one({
            "email": email,
            "created_on": datetime.now(IST).isoformat(),
        })
        user_id = str(result.inserted_id)


    today=date.today()
    payload = {
        "user_id":user_id,
        "email": email,
        "role": "user",
        "exp": datetime(today.year + (1 if today.month > 6 else 0),6,30, 18,30)
    }
    
    access_token = create_access_token(payload)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



@router.post("/admin")
def google_auth_admin(data: dict):


    idinfo = verify_google_token(data)
    email = idinfo["email"]

    admin, admin_id, email = verify_admin_by_email(email, "Y")


    today=date.today()
    payload = {
        "admin_id":str(admin_id),
        "email": email,
        "role": "admin",
        "exp": datetime(today.year + (1 if today.month > 6 else 0),6,30, 18,30)
    }
    
    access_token = create_access_token(payload)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



@router.post("/superadmin")
def google_auth_superadmin(data: dict):

    idinfo = verify_google_token(data)
    email = idinfo["email"]

    superadmin, superadmin_id, email = verify_superadmin_by_email(email, "Y")


    today=date.today()
    payload = {
        "superadmin_id":str(superadmin_id),
        "email": email,
        "role": "superadmin",
        "exp": datetime(today.year + (1 if today.month > 6 else 0),6,30, 18,30)
    }
    
    access_token = create_access_token(payload)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


