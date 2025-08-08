from api.core.database import owner
from bson import ObjectId

def create_owner(data: dict):
    result = owner.insert_one(data)
    return str(result.inserted_id)

async def get_owner_by_id(owner_id: str):
    return await owner.find_one({"_id": ObjectId(owner_id)})