from sqlalchemy import Column, Integer, String, Boolean , Date, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.user import user_skill

job_skill= Table(
    "job_skill",
    Base.metadata,
    Column("job_id",Integer, ForeignKey("jobs.id"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id"), primary_key=True)
)

class Skill(Base):
    __tablename__= "skills"
    id= Column(Integer, primary_key= True, index=True)
    name=Column(String, unique=True, index=True)
    category= Column(String, default="")
    
    #relationships
    users= relationship("User", secondary= user_skill, back_populates="skills")
    jobs= relationship("Job", secondary= job_skill, back_populates="required_skills")