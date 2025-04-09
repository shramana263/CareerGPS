from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session


app= FastAPI(
    title="JOB RECOMMENDATION SYSTEM",
    # openapi_url=
)


#set up cors
origins = [
    "http://localhost:3000",
    "https://job-recommendation-system-frontend.vercel.app"
]


@app.get("/")
def read_root():
    return {"message":"Welcome to the Job Recommendation System API!"}