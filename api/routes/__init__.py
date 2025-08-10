from fastapi import APIRouter
from . import consumer, distributor, forecast, owner, product, stock, transaction, warung, whatsapp

api_router = APIRouter()

api_router.include_router(consumer.router, prefix="/consumer", tags=["Consumers"])
api_router.include_router(distributor.router, prefix="/distributor", tags=["Distributors"])
api_router.include_router(forecast.router, prefix="/forecast", tags=["Forecast"])
api_router.include_router(owner.router, prefix="/owner", tags=["Owners"])
api_router.include_router(product.router, prefix="/product", tags=["Products"])
api_router.include_router(stock.router, prefix="/stock", tags=["Stocks"])
api_router.include_router(transaction.router, prefix="/transaction", tags=["Transactions"])
api_router.include_router(warung.router, prefix="/warung", tags=["Warung"])
api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["Whatsapp"])