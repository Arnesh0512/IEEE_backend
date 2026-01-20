from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from verify.token import verify_access_token
from verify.sudo import verify_sudo_payload
from utils.pattern import verify_session_db, DB_PATTERN
from fastapi.responses import StreamingResponse
from bson import ObjectId
from database import client
from gridfs import GridFS

security = HTTPBearer()
router = APIRouter(prefix="/root/getEvent", tags=["GetEvent"])






@router.get("/all-events")
def get_all_events_all_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)

    result = {}

    db_names = client.list_database_names()

    for db_name in db_names:
        if not DB_PATTERN.match(db_name):
            continue

        try:
            session_db_name = verify_session_db(db_name)
        except Exception:
            continue

        db = client[session_db_name]
        event_collection = db["event"]

        events_cursor = event_collection.find(
            {},
            {
                "event_name": 1,
                "event_date": 1,
                "registered_user": 1,
                "registered_team": 1,
                "remarked_user": 1,
                "remarked_team": 1,
                "remark": 1
            }
        )

        events = []
        for event in events_cursor:
            events.append({
                "event_id": str(event["_id"]),
                "event_name": event.get("event_name"),
                "event_date": event.get("event_date"),
                "no_of_registered_user": len(event.get("registered_user", [])),
                "no_of_registered_team": len(event.get("registered_team", [])),
                "no_of_remarked_user": len(event.get("remarked_user", [])),
                "no_of_remarked_team": len(event.get("remarked_team", [])),
                "remark": event.get("remark")
            })

        result[session_db_name] = {
            "count": len(events),
            "data": events
        }

    return {
        "success": True,
        "data": result
    }




@router.get("/{year}")
def get_all_events_of_year(
    year: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)

    year = verify_session_db(year)
    db = client[year]
    event_collection = db["event"]

    events_cursor = event_collection.find(
        {},
        {
            "event_name": 1,
            "event_date": 1,
            "registered_user": 1,
            "registered_team": 1,
            "remarked_user": 1,
            "remarked_team": 1
        }
    )

    events = []

    for event in events_cursor:
        events.append({
            "event_id": str(event["_id"]),
            "event_name": event.get("event_name"),
            "event_date": event.get("event_date"),
            "no_of_registered_user": len(event.get("registered_user", [])),
            "no_of_registered_team": len(event.get("registered_team", [])),
            "no_of_remarked_user": len(event.get("remarked_user", [])),
            "no_of_remarked_team": len(event.get("remarked_team", [])),
            "remark": event.get("remark")
        })

    return {
        "success": True,
        "year": year,
        "count": len(events),
        "data": events
    }


@router.get("/image/{year}/{image_id}")
def get_archive_image(
    year: str,
    image_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)  # sudo check

    db = client[year]

    archive_fs = GridFS(db)
    try:
        grid_out = archive_fs.get(ObjectId(image_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Image not found")

    return StreamingResponse(
        grid_out,
        media_type=grid_out.content_type or "image/jpeg"
    )



@router.get("/{year}/{event_id}")
def get_event_details(
    year: str,
    event_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)

    year = year.strip()
    db = client[year]

    event_collection = db["event"]
    user_collection = db["user"]
    team_collection = db["team"]

    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid event_id")
    event_oid = ObjectId(event_id)

    event = event_collection.find_one({"_id": event_oid})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    registered_user_ids = event.get("registered_user", [])
    registered_team_ids = event.get("registered_team", [])

    remarked_user_ids = event.get("remarked_user", [])
    remarked_team_ids = event.get("remarked_team", [])

    users_cursor = user_collection.find(
        {"_id": {"$in": registered_user_ids}},
        {"_id": 1, "email": 1, "name": 1, "registered_event": 1}
    )
    user_map = {u["_id"]: u for u in users_cursor}

    teams_cursor = team_collection.find(
        {"_id": {"$in": registered_team_ids}},
        {"_id": 1, "team_name": 1, "registered_on": 1, "remark":1}
    )
    team_map = {t["_id"]: t for t in teams_cursor}

    users_list = []
    for uid in registered_user_ids:
        user = user_map.get(uid)
        if not user:
            continue

        reg = next((r for r in user.get("registered_event", []) if r.get("event_id") == event_oid), {})
        
        users_list.append({
            "user_id": str(uid),
            "email": user.get("email"),
            "name": user.get("name"),
            "registered_on": reg.get("registered_on"),
            "remark": reg.get("remark", None)
        })

    teams_list = []
    for tid in registered_team_ids:
        team = team_map.get(tid)
        if not team:
            continue

        teams_list.append({
            "team_id": str(tid),
            "team_name": team.get("team_name"),
            "registered_on": team.get("registered_on"),
            "remark": team.get("remark", None)

        })

    event["_id"] = str(event["_id"])
    event["registered_user"] = users_list
    event["registered_team"] = teams_list
    event.pop("remarked_user",None)
    event.pop("remarked_team",None)
    event["event_thumbnail_id"] = str(event.get("event_thumbnail_id"))



    return {
        "success": True,
        "year": year,
        "data": event
    }
