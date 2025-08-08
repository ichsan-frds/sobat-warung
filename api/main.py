from fastapi import FastAPI
from .routes import api_router

app = FastAPI(title="Sobat Warung")

app.include_router(api_router, prefix="/api/v1")