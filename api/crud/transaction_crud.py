from api.core.database import transaction
from bson import ObjectId

def create_transaction(data: dict):
    result = transaction.insert_one(data)
    return str(result.inserted_id)

async def get_transaction_by_id(transaction_id: str):
    return await transaction.find_one({"_id": ObjectId(transaction_id)})