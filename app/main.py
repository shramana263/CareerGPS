# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from app.core.config import settings
from app.db.database import engine
from app.db.base_class import Base
from app.api.routes import auth, skills, jobs, applications, users

from app.db.database import SessionLocal
from app.services.job_sync import JobSyncService


# Create all tables in the database
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup logic
    logging.info("Starting job sync service...")
    try:
        db = SessionLocal()
        job_sync = JobSyncService(db)
        await job_sync.schedule_sync(interval_hours=12)
    except Exception as e:
        logging.error(f"Failed to start job sync: {str(e)}")
        db.close()
        raise
    yield
    # Shutdown logic
    logging.info("Shutting down job sync service...")
    if 'db' in locals():
        db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# app = FastAPI(
#     title=settings.PROJECT_NAME,
#     openapi_url=f"{settings.API_V1_STR}/openapi.json"
# )

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routes
app.include_router(auth.router, tags=["authentication"], prefix=f"{settings.API_V1_STR}/auth")
app.include_router(users.router, tags=["users"], prefix=f"{settings.API_V1_STR}/users")
app.include_router(skills.router, tags=["skills"], prefix=f"{settings.API_V1_STR}/skills")
app.include_router(jobs.router, tags=["jobs"], prefix=f"{settings.API_V1_STR}/jobs")
app.include_router(applications.router, tags=["applications"], prefix=f"{settings.API_V1_STR}/applications")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Job Recommendation System API"}

# Run with: uvicorn app.main:app --reload

# Start job sync on application startup
# @app.on_event("startup")
# def start_job_sync():
#     db = SessionLocal()
#     job_sync = JobSyncService(db)
#     job_sync.schedule_sync(interval_hours=12)