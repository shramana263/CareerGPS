import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import random
from sqlalchemy.orm import Session
from app.models.job import Job
from app.models.skill import Skill


class JobScraper:
    """Base class for job scrapers"""
    
    def __init__(self, db: Session):
        self.db = db
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def extract_skills_from_description(self, description: str) -> List[str]:
        """
        Extract skills from job description using a simple keyword approach.
        In a production environment, this would be replaced with a more sophisticated NLP approach.
        """
        # Common tech skills to look for (this is a simplified approach)
        common_skills = [
            "python", "javascript", "react", "node.js", "django", "flask", "sql", "postgresql",
            "mongodb", "aws", "docker", "kubernetes", "html", "css", "typescript", "java",
            "c++", "c#", "ruby", "php", "go", "swift", "kotlin", "rust", "scala", "r",
            "machine learning", "data science", "ai", "artificial intelligence", "deep learning",
            "devops", "ci/cd", "git", "agile", "scrum", "rest api", "graphql", "redux",
            "angular", "vue.js", "express", "spring", "asp.net", "laravel", "rails"
        ]
        
        description = description.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill in description:
                found_skills.append(skill)
        
        return found_skills
    
    def save_job_to_db(self, job_data: Dict[str, Any]) -> Job:
        """Save job data to database"""
         # Check for duplicate by URL or by title+company combination
        existing_job = self.db.query(Job).filter(
            (Job.url == job_data["url"]) |
            ((Job.title == job_data["title"]) & (Job.company == job_data["company"]))
        ).first()
    
        if existing_job:
        # Update existing job
            existing_job.description = job_data["description"]
            existing_job.location = job_data["location"]
            existing_job.salary_min = job_data.get("salary_min")
            existing_job.salary_max = job_data.get("salary_max")
            existing_job.job_type = job_data.get("job_type", "Full-time")
            existing_job.remote = job_data.get("remote", False)
            existing_job.updated_at = datetime.now()
            existing_job.is_active = True  # Ensure it's marked as active
            
            # Update skills
            # First, let's get the current skills
            current_skill_ids = {skill.id for skill in existing_job.required_skills}
            
            # Extract new skills
            skills_found = self.extract_skills_from_description(job_data["description"])
            for skill_name in skills_found:
                # Find or create skill
                skill = self.db.query(Skill).filter(Skill.name == skill_name).first()
                if not skill:
                    skill = Skill(name=skill_name)
                    self.db.add(skill)
                    self.db.commit()
                
                # Add skill to job if not already there
                if skill.id not in current_skill_ids:
                    existing_job.required_skills.append(skill)
            
            self.db.commit()
            self.db.refresh(existing_job)
            return existing_job
    
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
        
        # Extract and add skills
        skills_found = self.extract_skills_from_description(job_data["description"])
        for skill_name in skills_found:
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
    
    def scrape_jobs(self) -> List[Job]:
        """
        Implement in subclasses to scrape jobs from different sources
        """
        raise NotImplementedError("Subclasses must implement scrape_jobs method")

class IndeedScraper(JobScraper):
    """Scraper for Indeed job listings"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.base_url = "https://www.indeed.com"
    
    def scrape_jobs(self, keywords: str, location: str, limit: int = 20) -> List[Job]:
        """
        Scrape jobs from Indeed
        
        Parameters:
        keywords (str): Job keywords or title
        location (str): Job location
        limit (int): Maximum number of jobs to scrape
        
        Returns:
        List[Job]: List of scraped jobs saved to database
        """
        # Note: This is a simplified example. In a real application, you'd need to handle pagination, 
        # captchas, and other complexities of web scraping
        
        search_url = f"{self.base_url}/jobs?q={keywords}&l={location}"
        saved_jobs = []
        
        try:
            response = requests.get(search_url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = soup.find_all('div', class_='jobsearch-SerpJobCard')
                
                for job_card in job_cards[:limit]:
                    title_element = job_card.find('h2', class_='title')
                    if not title_element:
                        continue
                    
                    title = title_element.get_text().strip()
                    company_element = job_card.find('span', class_='company')
                    company = company_element.get_text().strip() if company_element else "Unknown"
                    
                    # Get job URL
                    job_url = self.base_url + title_element.find('a')['href']
                    
                    # Get job details
                    job_details = self.get_job_details(job_url)
                    if not job_details:
                        continue
                    
                    # Combine all job data
                    job_data = {
                        "title": title,
                        "company": company,
                        "location": location,
                        "description": job_details["description"],
                        "url": job_url,
                        "source": "Indeed",
                        "remote": "remote" in title.lower() or "remote" in job_details["description"].lower(),
                        "job_type": "Full-time"  # Default, could be extracted from description
                    }
                    
                    # Save to database
                    saved_job = self.save_job_to_db(job_data)
                    saved_jobs.append(saved_job)
                    
                    # Be nice to the server
                    time.sleep(random.uniform(1, 3))
        
        except Exception as e:
            print(f"Error scraping Indeed: {str(e)}")
        
        return saved_jobs
    
    def get_job_details(self, job_url: str) -> Optional[Dict[str, str]]:
        """Get detailed job information from job page"""
        try:
            response = requests.get(job_url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract job description
                description_div = soup.find('div', id='jobDescriptionText')
                if not description_div:
                    return None
                
                description = description_div.get_text().strip()
                
                return {
                    "description": description
                }
        
        except Exception as e:
            print(f"Error getting job details: {str(e)}")
        
        return None

# You could implement more scrapers for other job sites (LinkedIn, Glassdoor, etc.)
# class LinkedInScraper(JobScraper):
#     ...