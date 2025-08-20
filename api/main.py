import os
from fastapi import FastAPI
from api.routes import api_router

app = FastAPI(title="Sobat Warung")

app.run(port=int(os.environ.get("PORT", 8080)),host='0.0.0.0',debug=True)

app.include_router(api_router, prefix="/api/v1")

@app.get("/sanity")
def sanity_test():
    return {"message": "Hello, I'm Sobat Warung API"}