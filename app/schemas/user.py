from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date
from app.schemas.skill import Skill

class UserBase(BaseModel):
    email:EmailStr
    full_name:Optional[str]=None
    is_active:Optional[bool]= True
    experience_years: Optional[int] = 0
    education: Optional[str] = None
    
class UserCreate(UserBase):
    password:str
    
class UserUpdate(UserBase):
    password: Optional[str] = None
    
class UserInDB(UserBase):
    id:int
    hashed_password:str
    
class User(UserBase):
    id:int
    skills:List[Skill]=[]
    
    class Config:
        # orm_mode= True
        from_attributes = True 