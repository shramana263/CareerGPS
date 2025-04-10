from typing import List, Dict, Any, Optional
import requests
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.job import Job
from app.models.skill import Skill
from app.services.job_scrapers import JobScraper

class APIJobCollector:
    """Base class for collecting jobs from APIs"""
    
    def __init__(self, db: Session, api_key: str):
        self.db = db
        self.api_key = api_key
    
    def save_job(self, job_data: Dict[str, Any]) -> Job:
        """Save job to database with associated skills"""
        # Create job instance
        db_job = Job(
            title=job_data["title"],
            company=job_data["company"],
            location=job_data["location"],
            description=job_data["description"],
            salary_min=job_data.get("salary_min"),
            salary_max=job_data.get("salary_max"),
            job_type=job_data.get("job_type", "Full-time"),
            remote=job_data.get("remote", False),
            url=job_data["url"],
            source=job_data["source"],
            posted_date=job_data.get("posted_date", datetime.now())
        )
        
        # Process skills
        if "skills" in job_data and job_data["skills"]:
            for skill_name in job_data["skills"]:
                # Find or create skill
                skill = self.db.query(Skill).filter(Skill.name == skill_name).first()
                if not skill:
                    skill = Skill(name=skill_name)
                    self.db.add(skill)
                    self.db.commit()
                
                # Add skill to job
                db_job.required_skills.append(skill)
        
        # Save to database
        self.db.add(db_job)
        self.db.commit()
        self.db.refresh(db_job)
        
        return db_job
    
    def collect_jobs(self) -> List[Job]:
        """
        Implement in subclasses to collect jobs from different APIs
        """
        raise NotImplementedError("Subclasses must implement collect_jobs method")

# Example for Adzuna API
class AdzunaJobCollector(APIJobCollector):
    """Collect jobs from Adzuna API"""
    
    def __init__(self, db: Session, app_id: str, api_key: str):
        super().__init__(db, api_key)
        self.app_id = app_id
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
    
    def collect_jobs(
        self, 
        country: str = "us", 
        keywords: str = "software developer", 
        location: str = "", 
        page: int = 1, 
        results_per_page: int = 20
    ) -> List[Job]:
        """
        Collect jobs from Adzuna API
        
        Parameters:
        country (str): Country code (us, gb, etc.)
        keywords (str): Search keywords
        location (str): Location filter
        page (int): Page number
        results_per_page (int): Number of results per page
        
        Returns:
        List[Job]: List of jobs saved to database
        """
        url = f"{self.base_url}/{country}/search/{page}"
        
        params = {
            "app_id": self.app_id,
            "app_key": self.api_key,
            "results_per_page": results_per_page,
            "what": keywords
        }
        
        if location:
            params["where"] = location
        
        saved_jobs = []
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                for job_data in data.get("results", []):
                    # Extract job details
                    description = job_data.get("description", "")
                    
                    # Extract skills using NLP (simplified here)
                    scraper = JobScraper(self.db)
                    skills = scraper.extract_skills_from_description(description)
                    
                    # Format job data
                    formatted_job = {
                        "title": job_data.get("title", ""),
                        "company": job_data.get("company", {}).get("display_name", "Unknown"),
                        "location": job_data.get("location", {}).get("display_name", ""),
                        "description": description,
                        "url": job_data.get("redirect_url", ""),
                        "source": "Adzuna API",
                        "remote": "remote" in description.lower(),
                        "job_type": "Full-time",  # Default
                        "salary_min": job_data.get("salary_min"),
                        "salary_max": job_data.get("salary_max"),
                        "posted_date": datetime.strptime(job_data.get("created", ""), "%Y-%m-%dT%H:%M:%SZ") 
                                      if "created" in job_data else datetime.now(),
                        "skills": skills
                    }
                    
                    # Save to database
                    saved_job = self.save_job(formatted_job)
                    saved_jobs.append(saved_job)
        
        except Exception as e:
            print(f"Error collecting jobs from Adzuna: {str(e)}")
        
        return saved_jobs
