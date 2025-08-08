from pydantic import BaseModel

class OwnerCreate(BaseModel):
    owner_id: str
    phone_number: str
    owner_name: str
    state: str

class OwnerOut(OwnerCreate):
    id: str