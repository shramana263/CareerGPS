from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.base import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.application import Application
from app.models.job import Job
from app.schemas.application import ApplicationCreate, Application as ApplicationSchema, ApplicationUpdate

router = APIRouter()

@router.get("/", response_model=List[ApplicationSchema])
def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    applications = db.query(Application).filter(Application.user_id == current_user.id).all()
    return applications

@router.post("/", response_model=ApplicationSchema)
def apply_for_job(
    application: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # Check if job exists
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if already applied
    existing_application = db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.job_id == application.job_id
    ).first()
    
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this job"
        )
    
    # Create new application
    db_application = Application(
        user_id=current_user.id,
        job_id=application.job_id,
        cover_letter=application.cover_letter
    )
    
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application