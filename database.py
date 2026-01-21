
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from gridfs import GridFS
from datetime import datetime
from utils.reader import uri

client = MongoClient(uri, server_api=ServerApi('1'))

def current_session():
    end_year = datetime.now().year if datetime.now().month < 7 else datetime.now().year + 1
    start_yr = end_year - 1
    db_name = str(start_yr)+"_"+str(end_year)
    return db_name

def get_current_db():
    db_name = current_session()
    return client[db_name]


def current_user_collection():
    return get_current_db()["user"]

def current_event_collection():
    return get_current_db()["event"]

def current_team_collection():
    return get_current_db()["team"]

def current_fs_collection():
    return GridFS(get_current_db())


def current_admin_collection():
    cred_db = client["credentials"]
    admin_collection = cred_db["admin_"+current_session()]
    return admin_collection

def current_superadmin_collection():
    cred_db = client["credentials"]
    superadmin_collection = cred_db["superadmin"]
    return superadmin_collection



