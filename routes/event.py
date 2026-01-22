from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from bson import ObjectId
from database import current_event_collection, current_fs_collection, current_team_collection, current_user_collection
from schemas.event import EventCreate
from verify.token import verify_access_token
from verify.sudo import verify_sudo_payload
from verify.event import verify_event
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import date, time, datetime
from utils.time import IST



security = HTTPBearer()

router = APIRouter(prefix="/root/events", tags=["Events"])

MAX_IMAGE_SIZE = 50 * 1024




def normalize_event_dates(data: dict):
    if "event_date" in data and isinstance(data["event_date"], date):
        data["event_date"] = data["event_date"].isoformat()

    if "last_date_to_register" in data and isinstance(data["last_date_to_register"], date):
        data["last_date_to_register"] = data["last_date_to_register"].isoformat()

    if "event_time" in data and isinstance(data["event_time"], time):
        data["event_time"] = data["event_time"].isoformat()

    return data















@router.post("")
def create_event(
    event: EventCreate = Depends(EventCreate.convert_to_form),
    image: UploadFile | None = File(None),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)

    event_data = event.model_dump(exclude_none=True)
    event_data = normalize_event_dates(event_data)
    event_data["registered_user"] = []

    if event_data["event_team_allowed"] == True:
        event_data["registered_team"] = []
        if event_data["event_team_size"]<=0:
            event_data["event_team_size"]=1
    else:
        event_data["event_team_size"]=0

    if image:

        image.file.seek(0, 2)
        size = image.file.tell()
        image.file.seek(0)
        if size > MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail="Image size exceeds 50KB")

        fs = current_fs_collection()
        file_id = fs.put(
            image.file,
            filename=image.filename,
            content_type=image.content_type
        )
        event_data["event_thumbnail_id"] = str(file_id)

    event_data["created_on"] = datetime.now(IST).isoformat()

    event_collection = current_event_collection()
    event_collection.insert_one(event_data)
    return {"message": "Event created"}





@router.patch("/{event_id}")
def update_event(
    event_id: str,
    event_data: EventCreate = Depends(EventCreate.convert_to_form),
    image: UploadFile | None = File(None),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)

    event, event_id = verify_event(event_id)

    update_data = event_data.model_dump(exclude_none=True)
    update_data = normalize_event_dates(update_data)

    if image:
        image.file.seek(0, 2)
        size = image.file.tell()
        image.file.seek(0)

        if size > MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail="Image size exceeds 50KB")

        fs = current_fs_collection()
        if "event_thumbnail_id" in event:
            fs.delete(ObjectId(event["event_thumbnail_id"]))

        file_id = fs.put(image.file)
        update_data["event_thumbnail_id"] = str(file_id)

    team_allowed = update_data.get("event_team_allowed")

    event_collection = current_event_collection()
    team_collection = current_team_collection()
    user_collection = current_user_collection()

    if team_allowed is True:
        update_data["registered_team"] = []
        if update_data.get("event_team_size", 0) <= 0:
            update_data["event_team_size"] = 1

    elif team_allowed is False:

        team_collection.delete_many(
            {"event_id": event_id}
        )
        user_collection.update_many(
            {"registered_event.event_id": event_id},
            {"$unset": {"registered_event.$[].team_id": ""}}
        )
        event_collection.update_one(
            {"_id": event_id},
            {"$unset": {"registered_team": ""},
             "$unset": {"remarked_team": ""}}
        )

        update_data["event_team_size"] = 0

    if update_data:
        result = event_collection.update_one(
            {"_id": event_id},
            {"$set": update_data}
        )
    else:
        result = None

    if result and result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")

    return {"message": "Event updated"}








@router.delete("/{event_id}")
def delete_event(
    event_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)

    event, event_id = verify_event(event_id)

    event_collection = current_event_collection()
    team_collection = current_team_collection()
    user_collection = current_user_collection()
    fs = current_fs_collection()

    if "event_thumbnail_id" in event:
        fs.delete(ObjectId(event["event_thumbnail_id"]))

    team_collection.delete_many(
        {"event_id": event_id}
    )

    user_collection.update_many(
        {},
        {
            "$pull": {
                "registered_event": {
                    "event_id": event_id
                }
            }
        }
    )

    event_collection.delete_one(
        {"_id": event_id}
    )

    return {
        "message": "Event deleted successfully",
        "event_id": str(event_id)
    }




