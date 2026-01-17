from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse
from bson import ObjectId
from database import event_collection, fs
from schemas.event import EventCreate

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("")
def create_event(
    event: EventCreate = Depends(EventCreate.convert_to_form),
    image: UploadFile | None = File(None)
):
    event_data = event.model_dump(exclude_none=True, mode="json")
    event_data["registered_user"] = []

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
    image: UploadFile | None = File(None)
):
    update_data = event.model_dump(exclude_none=True)

    if image:
        file_id = fs.put(image.file)
        update_data["event_thumbnail_id"] = str(file_id)

    result = event_collection.update_one(
        {"_id": ObjectId(event_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")

    return {"message": "Event updated"}


@router.delete("/{event_id}")
def delete_event(event_id: str):
    event = event_collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if "event_thumbnail_id" in event:
        fs.delete(ObjectId(event["event_thumbnail_id"]))

    event_collection.delete_one({"_id": ObjectId(event_id)})
    return {"message": "Event deleted"}


@router.get("")
def get_all_events():
    events = list(event_collection.find())

    for event in events:
        event["_id"] = str(event["_id"])
        if "event_thumbnail_id" in event:
            event["event_thumbnail_url"] = f"/events/image/{event['event_thumbnail_id']}"

    return events


@router.get("/image/{image_id}")
def get_event_image(image_id: str):
    try:
        grid_out = fs.get(ObjectId(image_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Image not found")

    return StreamingResponse(grid_out, media_type=grid_out.content_type)
