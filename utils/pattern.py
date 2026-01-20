import re
from fastapi import HTTPException, status
from database import client

DB_PATTERN = re.compile(r"^\d{4}_\d{4}$")


def verify_session_db(db_name: str) -> str:

    if not DB_PATTERN.match(db_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid database format. Expected YYYY_YYYY"
        )

    existing_dbs = client.list_database_names()

    if db_name not in existing_dbs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This Academic Session database does not exist"
        )

    return db_name


def verify_admin_collection(collection_name: str) -> str:

    if not DB_PATTERN.match(collection_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid collection format. Expected YYYY_YYYY"
        )

    collection_name = "admin_" + collection_name
    db = client["credentials"]
    existing_coll = db.list_collection_names()

    if collection_name not in existing_coll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This Academic Session collection does not exist"
        )

    return collection_name


