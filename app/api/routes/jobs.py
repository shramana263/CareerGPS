from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any, Optional

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.job import Job
from app.models.skill import Skill
from app.schemas.job import JobCreate, Job as JobSchema, JobUpdate
from app.services.job_recommendations import get_recommended_jobs

router = APIRouter()

@router.get("/", response_model=List[JobSchema])
def get_jobs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    title: Optional[str] = None,
    company: Optional[str] = None,
    location: Optional[str] = None,
    remote: Optional[bool] = None
) -> Any:
    query = db.query(Job).filter(Job.is_active == True)
    
    if title:
        query = query.filter(Job.title.ilike(f"%{title}%"))
    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if remote is not None:
        query = query.filter(Job.remote == remote)
    
    jobs = query.offset(skip).limit(limit).all()
    return jobs

@router.post("/", response_model=JobSchema)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
) -> Any:
    # Create the job without skills first
    db_job = Job(
        title=job.title,
        company=job.company,
        location=job.location,
        description=job.description,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        job_type=job.job_type,
        remote=job.remote,
        url=job.url,
        source=job.source
    )
    
    # Add skills
    for skill_id in job.required_skills_ids:
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if skill:
            db_job.required_skills.append(skill)
    
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@router.get("/recommended", response_model=List[JobSchema])
def get_job_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10
) -> Any:
    return get_recommended_jobs(db, current_user, limit)
