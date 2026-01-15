from fastapi import FastAPI, HTTPException, status, UploadFile, File,  Depends
from fastapi.responses import StreamingResponse
from database import user_collection, event_collection, fs
from userSchema import UserCreate
from eventSchema import EventCreate
from bson import ObjectId


app = FastAPI()



@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate):
    if user_collection.find_one({"email": user.email}):
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )


    user_collection.insert_one(user.model_dump(mode="json"))

    return {"message": "User registered successfully"}




@app.post("/events")
def create_event(
    event: EventCreate = Depends(EventCreate.as_form),
    image: UploadFile | None = File(None)):
    
    event_data = event.model_dump(exclude_none=True)

    if image:
        file_id = fs.put(
            image.file,
            filename=image.filename,
            content_type=image.content_type
        )
        event_data["event_thumbnail_id"] = str(file_id)

    event_collection.insert_one(event_data)
    return {"message": "Event created"}


@app.patch("/events/{event_id}")
def update_event(
    event_id: str,
    event: EventCreate = Depends(EventCreate.as_form),
    image: UploadFile | None = File(None)):

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


@app.delete("/events/{event_id}")
def delete_event(event_id: str):
    event = event_collection.find_one({"_id": ObjectId(event_id)})

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if "event_thumbnail_id" in event:
        fs.delete(ObjectId(event["event_thumbnail_id"]))

    event_collection.delete_one({"_id": ObjectId(event_id)})

    return {"message": "Event deleted"}


@app.get("/events")
def get_all_events():
    events = list(event_collection.find())

    for event in events:
        event["_id"] = str(event["_id"])
        if "event_thumbnail_id" in event:
            event["event_thumbnail_url"] = (
                f"/events/image/{event['event_thumbnail_id']}"
            )

    return events


@app.get("/events/image/{image_id}")
def get_event_image(image_id: str):
    try:
        grid_out = fs.get(ObjectId(image_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Image not found")

    return StreamingResponse(
        grid_out,
        media_type=grid_out.content_type
    )