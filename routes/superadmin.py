from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from database import current_admin_collection, client
from schemas.admin import AdminCreate
from utils.time import IST
from verify.token import verify_access_token
from verify.superadmin import verify_superadmin_payload
from verify.admin import verify_admin, verify_admin_by_email
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.pattern import verify_admin_collection, DB_PATTERN

security = HTTPBearer()

router = APIRouter(prefix="/super", tags=["Super"])


@router.post("/register-admin")
def create_admin(
    admin: AdminCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
    token = credentials.credentials
    payload = verify_access_token(token)

    superadmin, super_id,super_email = verify_superadmin_payload(payload)    
    

    admin_data = admin.model_dump(mode="json")
    admin_data["created_on"] = datetime.now(IST).isoformat()
    admin_data["created_by"] = {"super_id": super_id, "super_email":super_email}
    admin_data["email"] = admin.email.lower()


    verify_admin_by_email(admin_data["email"], "N")

    admin_collection = current_admin_collection()
    admin_collection.insert_one(admin_data)



    return {"message": "Admin registered successfully"}






@router.get("/all-admins")
def get_all_admins_all_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_superadmin_payload(payload)

    result = {}
    db = client["credentials"]
    coll_names = db.list_collection_names()

    for coll_name in coll_names:

        if not coll_name.startswith("admin_"):
            continue

        session = coll_name[6:]

        if not DB_PATTERN.match(session):
            continue

        admin_collection = db[coll_name]

        admins = list(admin_collection.find())

        for admin in admins:
            admin["_id"] = str(admin["_id"])
            if "created_by" in admin and "super_id" in admin["created_by"]:
                admin["created_by"]["super_id"] = str(
                    admin["created_by"]["super_id"]
                )

        result[session] = admins

    return {
        "success": True,
        "data": result
    }






@router.get("/{db_name}/admins")
def get_all_admins(
    db_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_superadmin_payload(payload)

    coll_name = verify_admin_collection(db_name)
    db = client["credentials"]
    admin_collection = db[coll_name]

    admins = list(admin_collection.find())

    for admin in admins:
        admin["_id"] = str(admin["_id"])
        if "created_by" in admin and "super_id" in admin["created_by"]:
            admin["created_by"]["super_id"] = str(admin["created_by"]["super_id"])

    return {
        "success": True,
        "data": admins
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

    admin, admin_obj_id, admin_email = verify_admin(admin_id, email, "Y")

    admin_collection = current_admin_collection()
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
