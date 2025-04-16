from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from app.schemas.skill import Skill

class JobBase(BaseModel):
    title: str
    company: str
    location: str
    description: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_type: str
    remote: Optional[bool] = False
    url: str
    source: str

class JobCreate(JobBase):
    required_skills_ids: List[int]

class JobUpdate(JobBase):
    required_skills_ids: Optional[List[int]] = None

class Job(JobBase):
    id: int
    posted_date: datetime
    is_active: bool
    required_skills: List[Skill] = []
    match_score: Optional[float] = None  # Added for recommendation system
    
    class Config:
        # orm_mode = True
        from_attributes = True 