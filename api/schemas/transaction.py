from pydantic import BaseModel
from datetime import date

class TransactionCreate(BaseModel):
    date: date
    warung_id: str
    product_id: str
    quantity_sold: int
    total_price: float

class TransactionOut(TransactionCreate):
    transaction_id: str