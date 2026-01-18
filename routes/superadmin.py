from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from database import admin_collection
from schemas.admin import AdminCreate
from utils.time import IST
from utils.validate import verify_access_token
from utils.verify import verify_superadmin_payload, verify_admin
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

    super_id,super_email = verify_superadmin_payload(payload)    
    

    admin_data = admin.model_dump(mode="json")
    admin_data["created_on"] = datetime.now(IST).isoformat()
    admin_data["created_by"] = {"super_id": super_id, "super_email":super_email}
    admin_data["email"] = admin.email.lower()


    if admin_collection.find_one({"email": admin_data["email"]}):
        raise HTTPException(status_code=400, detail="Admin already exists")

    admin_collection.insert_one(admin_data)



    return {"message": "Admin registered successfully"}











@router.get("/admins")
def get_all_admins(
    credentials: HTTPAuthorizationCredentials = Depends(security)
    ):

    token = credentials.credentials
    payload = verify_access_token(token)
    verify_superadmin_payload(payload)

    admins = list(admin_collection.find())

    for admin in admins:
        admin["_id"] = str(admin["_id"])
        admin["created_by"]["super_id"] = str(admin["created_by"]["super_id"])

    return admins








@router.delete("/delete-admin")
def delete_admin(
    admin_id: str,
    email: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)

    verify_superadmin_payload(payload)

    admin_obj_id, admin_email = verify_admin(admin_id, email)

    result = admin_collection.delete_one({
        "_id": admin_obj_id,
        "email": admin_email
    })

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )

    return {"message": "Admin deleted successfully"}
