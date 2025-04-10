from pydantic import BaseModel
from typing import Optional

class SkillBase(BaseModel):
    name:str
    category:Optional[str]= None
    
class SkillCreate(SkillBase):
    pass
class SkillUpdate(SkillBase):
    pass
class Skill(SkillBase):
    id: int
    class Config:
        orm_mode=True