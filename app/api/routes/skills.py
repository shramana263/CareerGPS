from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.skill import Skill
from app.schemas.skill import SkillCreate, Skill as SkillSchema

router = APIRouter()

@router.get("/", response_model=List[SkillSchema])
def get_skills(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    skills = db.query(Skill).offset(skip).limit(limit).all()
    return skills

@router.post("/", response_model=SkillSchema)
def create_skill(
    skill: SkillCreate,
    db: Session = Depends(get_db),
) -> Any:
    db_skill = db.query(Skill).filter(Skill.name == skill.name).first()
    if db_skill:
        return db_skill
    db_skill = Skill(name=skill.name, category=skill.category)
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill

@router.post("/add-to-user/{skill_id}", response_model=SkillSchema)
def add_skill_to_user(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    current_user.skills.append(skill)
    db.commit()
    return skill