from pymongo import AsyncMongoClient

client = AsyncMongoClient("localhost", 27017)
db = client["sobat-warung-dummy"]

owner = db["owner"]
warung = db["warung"]