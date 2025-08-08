from .config import settings
from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi

client = AsyncMongoClient(settings.MONGODB_URL, server_api=ServerApi("1"))
db = client[settings.DB_NAME]

consumer = db["consumer"]
distributor = db["distributor"]
forecast = db["forecast"]
owner = db["owner"]
product = db["product"]
stock = db["stock"]
transaction = db["transaction"]
warung = db["warung"]