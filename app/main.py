# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import engine, Base
from app.api.routes import auth, skills, jobs, applications, users

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

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