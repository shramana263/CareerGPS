from sqlalchemy import Column, Integer, String, Boolean,Float , DateTime, Table, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.models.skill import job_skill


class Job(Base):
    __tablename__= "jobs"
    id= Column(Integer, primary_key=True, index= True)
    title= Column(String, index= True)
    company= Column(String, index= True)
    location =Column(String, index=True)
    description= Column(Text)
    salary_min= Column(Float, nullable=True)
    salary_max= Column(Float, nullable=True)
    job_type= Column(String)
    remote= Column(Boolean, default=False)
    url=Column(String)
    posted_date= Column(DateTime, default= func.now())
    is_active=Column(Boolean, default=True)
    source= Column(String)
    
    #relationships
    required_skills= relationship("Skill", secondary= job_skill, back_populates="jobs")
    applications= relationship("Application", back_populates="job")