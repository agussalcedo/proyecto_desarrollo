"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI

from app.core.config import settings
from app.core.database import check_db_connection 
from app.routes.user_routes import router as user_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.include_router(user_router)


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI MVC Application"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
