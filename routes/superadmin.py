from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from database import admin_collection, superadmin_collection
from schemas.admin import AdminCreate
from bson import ObjectId
from utils.time import IST
from utils.validate import verify_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

router = APIRouter(prefix="/super", tags=["Super"])




@router.post("/register-admin")
def create_admin(
    admin: AdminCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
    token = credentials.credentials
    payload = verify_access_token(token)

    super_id = payload.get("superadmin_id")
    super_email = payload.get("email").lower()

    if not super_id or not super_email:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    if payload.get("role") != "superadmin":
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    exists = superadmin_collection.find_one({
        "_id": ObjectId(super_id),
        "email": super_email
    })
    if not exists:
        raise HTTPException(status_code=404, detail="SuperAdmin not found")
    
    

    admin_data = admin.model_dump(mode="json")
    admin_data["created_on"] = datetime.now(IST).isoformat()
    admin_data["created_by"] = ObjectId(super_id)
    admin_data["email"] = admin.email.lower()


    if admin_collection.find_one({"email": admin_data["email"]}):
        raise HTTPException(status_code=400, detail="Admin already exists")

    admin_collection.insert_one(admin_data)



    return {"message": "Admin registered successfully"}




