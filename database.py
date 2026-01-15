
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from gridfs import GridFS
from dotenv import load_dotenv
import os

load_dotenv()  

uri = os.getenv("connection_string")

client = MongoClient(uri, server_api=ServerApi('1'))



db = client["IEEE"]
user_collection = db["user_reg"]
event_collection = db["event_reg"]
fs = GridFS(db)
