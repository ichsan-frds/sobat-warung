from fastapi import APIRouter, HTTPException
from api.schemas.owner import OwnerCreate, OwnerOut
from api.crud.owner_crud import create_owner, get_owner_by_id

router = APIRouter()

@router.get("/{owner_id}", response_model=OwnerOut)
async def get_owner_endpoint(owner_id: str):
    data = await get_owner_by_id(owner_id)
    if not data:
        raise HTTPException(status_code=404, detail="Owner Not Found")
    data["owner_id"] = str(data["_id"])
    
    return OwnerOut(**data)