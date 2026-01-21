from fastapi import HTTPException, status
from database import current_event_collection
from bson import ObjectId
from typing import Tuple
from datetime import datetime, time, timezone



def verify_event(event_id: str) -> Tuple[dict, ObjectId]:
    if not ObjectId.is_valid(event_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event_id"
        )
    
    event_oid = ObjectId(event_id)

    event_collection = current_event_collection()
    event = event_collection.find_one({"_id": event_oid})
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return (event,event_oid)



def verify_eventRegistry(
    event_id: ObjectId,
    user_id: ObjectId,
    type: str,
    user: dict,
    event: dict
):
    user_registered = any(
        reg.get("event_id") == event_id
        for reg in user.get("registered_event", [])
    )

    event_has_user = user_id in event.get("registered_user", [])

    if type == "Y":
        if not (user_registered and event_has_user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not registered for this event"
            )

    elif type == "N":
        if user_registered and event_has_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already registered for this event"
            )

    
def verify_can_register(
        event:dict
):
    if event["event_capacity"] == len(event["registered_user"]):
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No more user can register"
            )
    
    last_date = event["last_date_to_register"]
    last_date = datetime.fromisoformat(last_date).date()
    last_date = datetime.combine(
        last_date,
        time(18, 30, 0),
        tzinfo=timezone.utc
    )
    today = datetime.now(timezone.utc)

    if today>last_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration deadline has passed"
        )
