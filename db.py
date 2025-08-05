from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
load_dotenv()

URI = f"mongodb+srv://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@xplore.1v68hbs.mongodb.net/?retryWrites=true&w=majority&appName=xplore"

client = MongoClient(URI, server_api=ServerApi("1"))
db = client[os.getenv("DB_NAME")]

owner = db["owner"]
warung = db["warung"]

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)