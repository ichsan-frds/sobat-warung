from pydantic import BaseModel

class DistributorCreate(BaseModel):
    distributor_id: str
    distributor_name: str
    latitude: float
    longitude: float

class DistributorOut(DistributorCreate):
    id: str