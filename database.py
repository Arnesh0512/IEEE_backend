
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from gridfs import GridFS
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()  

uri = os.getenv("connection_string")

client = MongoClient(uri, server_api=ServerApi('1'))


end_year = datetime.now().year if datetime.now().month < 7 else datetime.now().year + 1
start_yr = end_year - 1
db_name = str(start_yr)+"-"+str(end_year)


db = client[db_name]
user_collection = db["user_reg"]
event_collection = db["event_reg"]
fs = GridFS(db)
