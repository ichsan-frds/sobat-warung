from pydantic import BaseModel

class ProductCreate(BaseModel):
    product_id: str
    product_name: str

class ProductOut(ProductCreate):
    id: str