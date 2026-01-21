from fastapi import HTTPException, status
from database import current_superadmin_collection
from bson import ObjectId
from bson.errors import InvalidId
from typing import Tuple

def verify_superadmin_payload(payload: dict) -> Tuple[dict|None, ObjectId, str]:

    superadmin_id = payload.get("superadmin_id")
    email = payload.get("email")
    role = payload.get("role")

    if not superadmin_id or not email or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    if role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a superadmin"
        )
    
    return verify_superadmin(superadmin_id, email, "Y")




def verify_superadmin(superadmin_id: str, email: str, type:str) -> Tuple[dict|None, ObjectId, str]:

    email = email.lower()

    try:
        superadmin_obj_id = ObjectId(superadmin_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid superadmin id"
        )

    superadmin_collection = current_superadmin_collection()
    superadmin = superadmin_collection.find_one({
        "_id": superadmin_obj_id,
        "email": email
    })

    if type == "N":
        if superadmin:
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Superadmin Already exists"
        )

    if type == "Y":
        if not superadmin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Superadmin not found"
            )
        

    return (superadmin,superadmin_obj_id,email)





def verify_superadmin_by_email(email: str, type: str) -> Tuple[dict|None, ObjectId|None, str]:
    email = email.lower()

    superadmin_collection = current_superadmin_collection()
    superadmin = superadmin_collection.find_one({
        "email": email
    })

    if type == "N":
        if superadmin:
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Superadmin Already exists"
        )
        superadmin_obj_id = None


    if type == "Y":
        if not superadmin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Superadmin not found"
            )
        superadmin_obj_id = superadmin["_id"]

    return (superadmin,superadmin_obj_id,email)



def verify_superadmin_by_id(superadmin_id: str, type: str) -> Tuple[dict|None, ObjectId, str|None]:

    try:
        superadmin_obj_id = ObjectId(superadmin_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid superadmin id"
        )

    superadmin_collection = current_superadmin_collection()
    superadmin = superadmin_collection.find_one({
        "_id": superadmin_obj_id,
    })

    if type == "N":
        if superadmin:
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Superadmin Already exists"
        )
        email = None

    if type == "Y":
        if not superadmin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Superadmin not found"
            )
        email=superadmin["email"]
        
    return (superadmin,superadmin_obj_id,email)