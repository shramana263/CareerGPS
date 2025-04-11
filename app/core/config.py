from pydantic import PostgresDsn
from typing import Optional
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str="/api/v1"
    PROJECT_NAME:str="Job Recommendation System"
    
    #database
    DATABASE_URL:str= os.getenv("DATABASE_URL")
    
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
        env_file = ".env"
    
    @property
    def sync_database_url(self) -> str:
        return str(self.DATABASE_URL)
        
settings= Settings()