from fastapi import APIRouter, HTTPException
from api.schemas.transaction import TransactionCreate, TransactionOut
from api.crud.transaction_crud import get_transaction_by_id

router = APIRouter()

@router.get("/{transaction_id}", response_model=TransactionOut)
async def get_transaction_endpoint(transaction_id: str):
    data = await get_transaction_by_id(transaction_id)
    if not data:
        raise HTTPException(status_code=404, detail="Transaction Not Found")
    data["transaction_id"] = str(data["_id"])
    
    return TransactionOut(**data)