from fastapi import APIRouter
from . import whatsapp

api_router = APIRouter()

api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["Whatsapp"])