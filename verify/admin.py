from fastapi import HTTPException, status
from database import admin_collection
from bson import ObjectId
from bson.errors import InvalidId
from typing import Tuple

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
            detail="Not a admin"
        )
    
    return verify_admin(admin_id, email, "Y")




def verify_admin(admin_id: str, email: str, type:str) -> Tuple[ObjectId, str]:

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

    if type == "N":
        if exists:
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admin Already exists"
        )

    if type == "Y":
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        

    return (admin_obj_id,email)





def verify_admin_by_email(email: str, type: str) -> Tuple[ObjectId|None, str]:
    email = email.lower()

    exists = admin_collection.find_one({
        "email": email
    })

    if type == "N":
        if exists:
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admin Already exists"
        )
        admin_obj_id = None


    if type == "Y":
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        admin_obj_id = exists["_id"]

    return (admin_obj_id,email)



def verify_admin_by_id(admin_id: str, type: str) -> Tuple[ObjectId, str|None]:

    try:
        admin_obj_id = ObjectId(admin_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin id"
        )

    exists = admin_collection.find_one({
        "_id": admin_obj_id,
    })

    if type == "N":
        if exists:
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admin Already exists"
        )
        email = None

    if type == "Y":
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        email=exists["email"]
        
    return (admin_obj_id,email)