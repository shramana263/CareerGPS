from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Any

from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.config import settings
from app.db.base import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, User as UserSchema

router= APIRouter()

@router.post("/regiser", response_model= UserSchema)
def register_user(user:UserCreate, db:Session= Depends(get_db))->Any:
    db_user= db.query(User).filter(User.email==user.email).first()
    if db_user:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        ) 
    hashed_password= get_password_hash(user.password)
    db_user=User(
        email= user.email,
        hashed_password=hashed_password,
        full_name= user.full_name,
        experience_years= user.experience_years,
        education= user.education
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            subject=user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
