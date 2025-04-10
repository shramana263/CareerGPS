from pydantic import BaseSettings, PostgresDsn
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str="/api/v1"
    PROJECT_NAME:str="Job Recommendation System"
    
    #database
    DATABASE_URL:PostgresDsn= os.getenv("DATABASE_URL")
    
    #authentication
    SECRET_KEY:str=os.getenv("SECRET_KEY","secret-key-for-dev")
    ALGORITHM:str=os.getenv("ALGORITHM","HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES:int=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30))
    
    
    #cors
    BACKEND_CORS_ORIGINS:list=[
        "http://localhost:3000",
        "http://localhost:8000"
    ]
    
    class Config:
        case_sensitive=True
        
settings= Settings()