from sqlalchemy.orm import Session
from typing import List
from app.models.user import User
from app.models.job import Job
from app.schemas.job import Job as JobSchema

def get_recommended_jobs(db: Session, user: User, limit: int = 10) -> List[JobSchema]:
    """
    Get job recommendations for a user based on their skills.
    
    Algorithm:
    1. Get user skills
    2. Find jobs that require these skills
    3. Calculate match score based on overlap of user skills and job required skills
    4. Sort jobs by match score
    5. Return top N jobs
    
    Parameters:
    db (Session): Database session
    user (User): User model instance
    limit (int): Maximum number of jobs to return
    
    Returns:
    List[JobSchema]: List of recommended jobs with match scores
    """
    # Get all active jobs
    all_jobs = db.query(Job).filter(Job.is_active == True).all()
    
    # Get set of user skill IDs for efficient lookup
    user_skill_ids = {skill.id for skill in user.skills}
    
    # If user has no skills, return empty list
    if not user_skill_ids:
        return []
    
    # Calculate match scores for each job
    job_matches = []
    for job in all_jobs:
        job_skill_ids = {skill.id for skill in job.required_skills}
        
        # If job has no required skills, skip it
        if not job_skill_ids:
            continue
        
        # Calculate match score
        matching_skills = user_skill_ids.intersection(job_skill_ids)
        match_score = len(matching_skills) / len(job_skill_ids) * 100
        
        # Only consider jobs with at least one matching skill
        if match_score > 0:
            # Convert to schema and add match score
            job_schema = JobSchema.from_orm(job)
            job_schema.match_score = match_score
            job_matches.append(job_schema)
    
    # Sort by match score (highest first)
    job_matches.sort(key=lambda x: x.match_score, reverse=True)
    
    # Return top N results
    return job_matches[:limit]