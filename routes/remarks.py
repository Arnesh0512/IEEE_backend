from fastapi import APIRouter, Depends, HTTPException, status
from database import current_event_collection, current_user_collection, current_team_collection
from verify.token import verify_access_token
from verify.sudo import verify_sudo_payload
from verify.event import verify_event, verify_eventRegistry
from verify.user import verify_user
from verify.team import verify_team_by_id
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

router = APIRouter(prefix="/root/remarks", tags=["Remarks"])

@router.patch("/user")
def create_user_remark(
    event_id: str,
    user_id: str,
    user_email: str,
    remark: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)

    user, user_id,user_email=verify_user(user_id, user_email,"Y")
    event, event_id=verify_event(event_id)
    verify_eventRegistry(event_id, user_id, "Y", user, event)

    user_collection = current_user_collection()
    user_collection.update_one(
    {
        "_id": user_id,
        "registered_event.event_id": event_id
    },
    {
        "$set": {
            "registered_event.$.remark": remark
        }
    }
    )
    event_collection = current_event_collection()
    event_collection.update_one(
    {"_id": event_id},
    {
        "$addToSet": {
            "remarked_user": user_id
        }
    }
    )
    
    return {"message": "Remark added"}


@router.delete("/user")
def delete_user_remark(
    event_id: str,
    user_id: str,
    user_email: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)

    user, user_id,user_email=verify_user(user_id, user_email,"Y")
    event, event_id=verify_event(event_id)
    verify_eventRegistry(event_id, user_id, "Y", user, event)

    if user_id not in event["remarked_user"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No remark for this user yet for this event"
        )

    user_collection = current_user_collection()
    user_collection.update_one(
    {
        "_id": user_id,
        "registered_event.event_id": event_id
    },
    {
        "$unset": {
            "registered_event.$.remark": ""
        }
    }
    )
    event_collection = current_event_collection()
    event_collection.update_one(
    {"_id": event_id},
    {
        "$pull": {
            "remarked_user": user_id
        }
    }
    )
    
    return {"message": "Remark deleted"}


@router.patch("/event")
def add_event_remark(
    event_id: str,
    remark: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)

    event, event_id=verify_event(event_id)

    event_collection = current_event_collection()
    event_collection.update_one(
    {
        "_id": event_id
    },
    {
        "$set": {
            "remark": remark
        }
    }
    )
    
    
    return {"message": "Remark added"}


@router.delete("/event")
def delete_event_remark(
    event_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)

    event, event_id=verify_event(event_id)
    if event.get("remark") == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no remark for this event yet"
        )

    event_collection = current_event_collection()
    event_collection.update_one(
    {
        "_id": event_id
    },
    {
        "$unset": {
            "remark": ""
        }
    }
    )
    
    return {"message": "Remark deleted"}


@router.patch("/team")
def add_team_remark(
    team_id: str,
    remark: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)

    team, team_id=verify_team_by_id(team_id)

    team_collection = current_team_collection()
    team_collection.update_one(
    {
        "_id": team_id
    },
    {
        "$set": {
            "remark": remark
        }
    }
    )
    event_collection = current_event_collection()
    event_collection.update_one(
    {"_id": team["event_id"]},
    {
        "$addToSet": {
            "remarked_team": team_id
        }
    }
    )
    
    return {"message": "Remark added"}


@router.delete("/team")
def delete_team_remark(
    team_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)

    team, team_id=verify_team_by_id(team_id)
    if team.get("remark") == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no remark for this team yet"
        )

    team_collection = current_team_collection()
    team_collection.update_one(
    {
        "_id": team_id
    },
    {
        "$unset": {
            "remark": ""
        }
    }
    )
    event_collection = current_event_collection()
    event_collection.update_one(
    {"_id": team["event_id"]},
    {
        "$pull": {
            "remarked_team": team_id
        }
    }
    )
    
    return {"message": "Remark deleted"}

