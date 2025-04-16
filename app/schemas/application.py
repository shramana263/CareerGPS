from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.application import ApplicationStatus

class ApplicationBase(BaseModel):
    job_id: int
    cover_letter: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(BaseModel):
    cover_letter: Optional[str] = None
    status: Optional[ApplicationStatus] = None

class Application(ApplicationBase):
    id: int
    user_id: int
    status: ApplicationStatus
    applied_date: datetime
    last_updated: datetime
    
    class Config:
        # orm_mode = True
        from_attributes = True 