import os 
from pymongo import MongoClient 
from dotenv import load_dotenv


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

client = None
db = None

def connection():
    global client, db
    if db is None:
        client= MongoClient(MONGO_URI)
        db= client[MONGO_DB_NAME]
    return db    