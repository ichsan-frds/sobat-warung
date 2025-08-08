from pydantic import BaseModel

class OwnerCreate(BaseModel):
    phone_number: str
    owner_name: str
    state: str

class OwnerOut(OwnerCreate):
    owner_id: str