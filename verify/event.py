from fastapi import HTTPException, status
from database import user_collection, event_collection
from bson import ObjectId
from typing import Tuple



def verify_event(event_id: str) -> Tuple[dict, ObjectId]:
    if not ObjectId.is_valid(event_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event_id"
        )
    
    event_oid = ObjectId(event_id)

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
        if user_registered or event_has_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already registered for this event"
            )

    
