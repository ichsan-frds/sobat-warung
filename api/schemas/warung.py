from pydantic import BaseModel

class WarungCreate(BaseModel):
    warung_id: str
    warung_name: str
    owner_id: str
    latitude: float
    longitude: float

class WarungOut(WarungCreate):
    id: str