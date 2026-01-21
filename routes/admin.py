from fastapi import APIRouter, Depends
from verify.token import verify_access_token
from verify.admin import verify_admin_payload
from verify.superadmin import verify_superadmin_payload
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/profile")
def get_admin_details(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_access_token(token)
    admin,admin_id ,email = verify_admin_payload(payload)

    admin.pop("_id", None)
    admin.pop("created_by", None)
    admin.pop("created_on",None)

    return {
        "success": True,
        "data": admin
    }

@router.get("/super/profile")
def get_admin_details(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_access_token(token)
    superadmin,superadmin_id ,email = verify_superadmin_payload(payload)

    superadmin.pop("_id", None)

    return {
        "success": True,
        "data": superadmin
    }