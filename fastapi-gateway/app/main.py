"""FastAPI entrypoint del gateway de autenticación."""

from fastapi import FastAPI
from app.api.v1.routes import router

# App principal del gateway: solo expone API de autenticación versionada.
app = FastAPI(
    title="FastAPI Gateway",
    version="1.0.0",
)

app.include_router(router)
