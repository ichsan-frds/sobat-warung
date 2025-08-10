from pydantic import BaseModel

class ForecastCreate(BaseModel):
    forecast_id: str
    warung_id: str
    product_id: str
    predicted_sell: int

class ForecastOut(ForecastCreate):
    id: str