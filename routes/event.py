from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from bson import ObjectId
from database import event_collection, fs
from schemas.event import EventCreate
from verify.token import verify_access_token
from verify.sudo import verify_sudo_payload
from verify.event import verify_event
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

router = APIRouter(prefix="/root/events", tags=["Events"])

@router.post("")
def create_event(
    event: EventCreate = Depends(EventCreate.convert_to_form),
    image: UploadFile | None = File(None),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)

    event_data = event.model_dump(exclude_none=True, mode="json")
    event_data["registered_user"] = []

    if event_data["event_team_allowed"] == True:
        event_data["registered_team"] = []

    if image:
        file_id = fs.put(
            image.file,
            filename=image.filename,
            content_type=image.content_type
        )
        event_data["event_thumbnail_id"] = str(file_id)

    event_collection.insert_one(event_data)
    return {"message": "Event created"}





@router.patch("/{event_id}")
def update_event(
    event_id: str,
    event: EventCreate = Depends(EventCreate.convert_to_form),
    image: UploadFile | None = File(None),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)


    update_data = event.model_dump(exclude_none=True)
    if image:
        if "event_thumbnail_id" in event:
            fs.delete(ObjectId(event["event_thumbnail_id"]))
        file_id = fs.put(image.file)
        update_data["event_thumbnail_id"] = str(file_id)


    event, event_id = verify_event(event_id)

    if update_data["event_team_allowed"] == True:
        update_data["registered_team"] = []
    else:
        event_collection.update_one(
            {"_id":event_id},
            {"$unset":{"registered_team": ""}}
        )

    result = event_collection.update_one(
        {"_id": event_id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")

    return {"message": "Event updated"}







@router.delete("/{event_id}")
def delete_event(event_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)

    event, event_id = verify_event(event_id)
    

    if "event_thumbnail_id" in event:
        fs.delete(ObjectId(event["event_thumbnail_id"]))

    event_collection.delete_one({"_id": event_id})
    return {"message": "Event deleted"}




