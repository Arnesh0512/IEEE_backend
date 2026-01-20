from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from verify.token import verify_access_token
from verify.sudo import verify_sudo_payload
from utils.pattern import verify_session_db, DB_PATTERN
from bson import ObjectId
from database import client

security = HTTPBearer()
router = APIRouter(prefix="/root/getTeam", tags=["GetTeam"])



@router.get("/all-teams")
def get_all_teams_all_sessions(
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
        team_collection = db["team"]
        user_collection = db["user"]
        event_collection = db["event"]

        teams = list(team_collection.find({}))
        if not teams:
            result[session_db_name] = {"count": 0, "data": []}
            continue

        event_ids = list({team["event_id"] for team in teams})
        leader_ids = list({team["leader_id"] for team in teams})

        events = {e["_id"]: e.get("event_name") for e in event_collection.find(
            {"_id": {"$in": event_ids}}, {"_id": 1, "event_name": 1})}
        leaders = {u["_id"]: {"name": u.get("name"), "email": u.get("email")} for u in user_collection.find(
            {"_id": {"$in": leader_ids}}, {"_id": 1, "name": 1, "email": 1})}

        session_result = []
        for team in teams:
            tid = team["_id"]
            eid = team["event_id"]
            lid = team["leader_id"]
            members = team.get("members", [])
            remark = team.get("remark")

            session_result.append({
                "team_id": str(tid),
                "team_name": team.get("team_name"),
                "event_name": events.get(eid),
                "leader_name": leaders.get(lid, {}).get("name"),
                "leader_email": leaders.get(lid, {}).get("email"),
                "number_of_members": len(members),
                "remark": remark
            })

        result[session_db_name] = {
            "count": len(session_result),
            "data": session_result
        }

    return {
        "success": True,
        "data": result
    }



@router.get("/{year}")
def get_all_teams_of_year(
    year: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)

    year = verify_session_db(year)
    db = client[year]

    team_collection = db["team"]
    user_collection = db["user"]
    event_collection = db["event"]

    teams = list(team_collection.find({}))

    if not teams:
        return {"success": True, "year": year, "count": 0, "data": []}

    event_ids = list({team["event_id"] for team in teams})
    leader_ids = list({team["leader_id"] for team in teams})

    events = {e["_id"]: e.get("event_name") for e in event_collection.find({"_id": {"$in": event_ids}}, {"_id": 1, "event_name": 1})}
    leaders = {u["_id"]: {"name": u.get("name"), "email": u.get("email")} for u in user_collection.find({"_id": {"$in": leader_ids}}, {"_id": 1, "name": 1, "email": 1})}

    result = []

    for team in teams:
        tid = team["_id"]
        eid = team["event_id"]
        lid = team["leader_id"]
        members = team.get("members", [])
        remark = team.get("remark")

        result.append({
            "team_id": str(tid),
            "team_name": team.get("team_name"),
            "event_name": events.get(eid),
            "leader_name": leaders.get(lid, {}).get("name"),
            "leader_email": leaders.get(lid, {}).get("email"),
            "number_of_members": len(members),
            "remark": remark
        })

    return {
        "success": True,
        "year": year,
        "count": len(result),
        "data": result
    }



@router.get("/{year}/{team_id}")
def get_team_details(
    year: str,
    team_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_access_token(token)
    verify_sudo_payload(payload)

    if not ObjectId.is_valid(team_id):
        raise HTTPException(status_code=400, detail="Invalid team_id")
    team_oid = ObjectId(team_id)

    year = verify_session_db(year)
    db = client[year]

    team_collection = db["team"]
    user_collection = db["user"]
    event_collection = db["event"]

    team = team_collection.find_one({"_id": team_oid})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    leader_id = team["leader_id"]
    event_id = team["event_id"]
    member_ids = team.get("members", [])

    users_cursor = user_collection.find({"_id": {"$in": [leader_id] + member_ids}}, {"_id": 1, "name": 1, "email": 1})
    users_map = {u["_id"]: {"name": u.get("name"), "email": u.get("email")} for u in users_cursor}

    event = event_collection.find_one({"_id": event_id}, {"_id": 1, "event_name": 1})
    event_name = event.get("event_name")

    members_list = []
    for mid in member_ids:
        user = users_map.get(mid)
        if user:
            members_list.append({
                "member_id": str(mid),
                "name": user.get("name"),
                "email": user.get("email")
            })

    response = {
        "team_id": str(team_oid),
        "team_name": team.get("team_name"),
        "leader": {
            "leader_id": str(leader_id),
            "name": users_map.get(leader_id, {}).get("name"),
            "email": users_map.get(leader_id, {}).get("email")
        },
        "event": {
            "event_id": str(event_id),
            "event_name": event_name
        },
        "members": members_list,
        "registered_on": team.get("registered_on"),
        "remark": team.get("remark")
    }

    return {
        "success": True,
        "year": year,
        "data": response
    }
