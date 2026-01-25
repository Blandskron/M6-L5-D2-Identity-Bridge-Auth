from fastapi import FastAPI
from app.api.v1.routes import router

app = FastAPI(
    title="FastAPI Gateway",
    version="1.0.0",
)

app.include_router(router)
