from fastapi import FastAPI
from api.routes import api_router

app = FastAPI(title="Sobat Warung")

app.include_router(api_router, prefix="/api/v1")

@app.get("/sanity")
def sanity_test():
    return {"message": "Hello, I'm Sobat Warung API"}