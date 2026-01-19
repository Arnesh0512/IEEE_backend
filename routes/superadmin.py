from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from database import admin_collection, client
from schemas.admin import AdminCreate
from utils.time import IST
from verify.token import verify_access_token
from verify.superadmin import verify_superadmin_payload
from verify.admin import verify_admin
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.pattern import verify_session_db, DB_PATTERN

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











@router.get("/{db_name}/admins")
def get_all_admins(
    db_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_superadmin_payload(payload)

    db_name = verify_session_db(db_name)
    db = client[db_name]
    admin_collection = db["admins"]

    admins = list(admin_collection.find())

    for admin in admins:
        admin["_id"] = str(admin["_id"])
        if "created_by" in admin and "super_id" in admin["created_by"]:
            admin["created_by"]["super_id"] = str(admin["created_by"]["super_id"])

    return {
        "success": True,
        "data": admins
    }




@router.get("/all/admins")
def get_all_admins_all_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_superadmin_payload(payload)

    result = {}

    db_names = client.list_database_names()

    for db_name in db_names:
        if not DB_PATTERN.match(db_name):
            continue

        db = client[db_name]
        admin_collection = db["admins"]

        admins = list(admin_collection.find())

        for admin in admins:
            admin["_id"] = str(admin["_id"])
            if "created_by" in admin and "super_id" in admin["created_by"]:
                admin["created_by"]["super_id"] = str(admin["created_by"]["super_id"])

        result[db_name] = admins

    return {
        "success": True,
        "data": result
    }








@router.delete("/delete-admin")
def delete_admin(
    admin_id: str,
    email: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)

    verify_superadmin_payload(payload)

    admin_obj_id, admin_email = verify_admin(admin_id, email, "Y")

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
