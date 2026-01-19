from fastapi import HTTPException, status
from bson import ObjectId
from typing import Tuple
from .admin import verify_admin_payload, verify_admin, verify_admin_by_email, verify_admin_by_id
from .superadmin import verify_superadmin_payload, verify_superadmin, verify_superadmin_by_email, verify_superadmin_by_id

def verify_sudo_payload(payload: dict) -> Tuple[dict|None, ObjectId, str, str]:

    role = payload.get("role")

    if not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    if role == "admin":
        sudo, sudo_id, sudo_email =  verify_admin_payload(payload)
    
    elif role == "superadmin":
        sudo, sudo_id, sudo_email =  verify_superadmin_payload(payload)


    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )
    
    return (sudo, sudo_id, sudo_email,role)
    




def verify_sudo(sudo_id: str, sudo_email: str, role:str, type:str) -> Tuple[dict|None, ObjectId, str]:

    if role == "admin":
        return verify_admin(sudo_id, sudo_email, type)
    
    elif role == "superadmin":
        return verify_superadmin(sudo_id, sudo_email, type)
    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )

    
    

def verify_sudo_by_email(sudo_email: str, role:str, type: str) -> Tuple[dict|None, ObjectId|None, str]:

    if role == "admin":
        return verify_admin_by_email(sudo_email, type)
    
    elif role == "superadmin":
        return verify_superadmin_by_email(sudo_email, type)
    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )
    




def verify_sudo_by_id(sudo_id: str, role:str, type: str) -> Tuple[dict|None, ObjectId, str|None]:

    if role == "admin":
        return verify_admin_by_id(sudo_id, type)
    
    elif role == "superadmin":
        return verify_superadmin_by_id(sudo_id, type)
    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )
