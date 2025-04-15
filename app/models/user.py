from sqlalchemy import Column, Integer, String, Boolean , Date, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


user_skill= Table(
    "user_skill",
    Base.metadata,
    Column("user_id",Integer, ForeignKey("users.id"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id"), primary_key=True)
)

class User(Base):
    __tablename__= "users"
    
    id= Column(Integer, primary_key= True, index= True)
    email= Column(String, unique= True, index= True)
    hashed_password = Column(String)
    full_name= Column(String)
    is_active= Column(Boolean, default=True)
    
    #Resume details 
    experience_years= Column(Integer, default=0)
    education= Column(String, default="")
    
    #relationships
    skills= relationship("Skill", secondary= user_skill, back_populates="users")
    applications= relationship("Application", back_populates="user")