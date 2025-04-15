from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.schemas.skill import Skill as SkillSchema

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def get_user_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    return current_user

@router.put("/me", response_model=UserSchema)
def update_user_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    for key, value in user_update.dict(exclude_unset=True).items():
        if key != "password" and value is not None:
            setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/me/skills", response_model=List[SkillSchema])
def get_my_skills(
    current_user: User = Depends(get_current_user),
) -> Any:
    return current_user.skills