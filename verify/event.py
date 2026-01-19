from fastapi import HTTPException, status
from database import user_collection, event_collection
from bson import ObjectId




def verify_event(event_id: str) -> ObjectId:
    if not ObjectId.is_valid(event_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event_id"
        )
    
    event_oid = ObjectId(event_id)

    if not event_collection.find_one({"_id": event_oid}):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return event_oid


def verify_eventRegistry(event_id: ObjectId, user_id:ObjectId, type:str):
    
    user_check = user_collection.find_one({
        "_id": user_id,
        "registered_event.event_id": event_id
    })

    event_check = event_collection.find_one({
        "_id": event_id,
        "registered_user": user_id
    })

    if type=="Y":
        if not user_check or event_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not registered for this event"
            )
        
    if type=="N":
        if user_check and event_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already registered for this event"
            )
    
