from pymongo import AsyncMongoClient, ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

URI = f"mongodb+srv://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@xplore.1v68hbs.mongodb.net/?retryWrites=true&w=majority&appName=xplore"

client = AsyncMongoClient(URI, server_api=ServerApi("1"))
db = client[os.getenv("DB_NAME")]

owner = db["owner"]
warung = db["warung"]