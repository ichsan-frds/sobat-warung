from pydantic import BaseModel
from datetime import date

class StockCreate(BaseModel):
    stock_id: str
    warung_id: str
    product_id: str
    stock_count: int
    price: float
    last_transaction: date

class StockOut(StockCreate):
    id: str