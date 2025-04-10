# app/services/job_sync.py
from sqlalchemy.orm import Session
from typing import List
import schedule
import time
import threading
from app.services.job_scrapers import IndeedScraper
from app.services.job_collectors import AdzunaJobCollector
from app.core.config import settings
from app.models.job import Job

class JobSyncService:
    """Service to sync jobs from various sources"""
    
    def __init__(self, db: Session):
        self.db = db
        self.scrapers = [
            IndeedScraper(db)
        ]
        
        # Initialize API collectors if API keys are available
        adzuna_app_id = getattr(settings, "ADZUNA_APP_ID", None)
        adzuna_api_key = getattr(settings, "ADZUNA_API_KEY", None)
        
        self.collectors = []
        if adzuna_app_id and adzuna_api_key:
            self.collectors.append(
                AdzunaJobCollector(db, adzuna_app_id, adzuna_api_key)
            )
    
    def sync_jobs(self):
        """Sync jobs from all sources"""
        print("Starting job sync...")
        
        current_job_ids = set()
        
        # Use scrapers
        for scraper in self.scrapers:
            try:
                # Example search terms
                search_terms = [
                    {"keywords": "python developer", "location": "remote"},
                    {"keywords": "react developer", "location": "remote"},
                    {"keywords": "full stack developer", "location": "remote"}
                ]
                
                for terms in search_terms:
                    jobs = scraper.scrape_jobs(**terms)
                    print(f"Scraped {len(jobs)} jobs for {terms['keywords']}")
                    # Add job IDs to current set
                    current_job_ids.update([job.id for job in jobs])
            
            except Exception as e:
                print(f"Error with scraper {type(scraper).__name__}: {str(e)}")
        
        # Use API collectors
        for collector in self.collectors:
            try:
                search_terms = [
                    {"keywords": "python developer"},
                    {"keywords": "react developer"},
                    {"keywords": "full stack developer"}
                ]
                
                for terms in search_terms:
                    jobs = collector.collect_jobs(**terms)
                    print(f"Collected {len(jobs)} jobs for {terms['keywords']}")
                    # Add job IDs to current set
                    current_job_ids.update([job.id for job in jobs])
            
            except Exception as e:
                print(f"Error with collector {type(collector).__name__}: {str(e)}")
         # Mark jobs not found in this sync as inactive
        self._mark_old_jobs_inactive(current_job_ids)
        
        # Remove very old inactive jobs
        self._remove_old_inactive_jobs(days=30)  # Keep inactive jobs for 30 days
        
        print("Job sync completed")
        
    def _mark_old_jobs_inactive(self, current_job_ids):
        """Mark jobs not found in the current sync as inactive"""
        if not current_job_ids:
            return
            
        old_jobs = self.db.query(Job).filter(
            Job.is_active == True,
            ~Job.id.in_(current_job_ids)
        ).all()
        
        for job in old_jobs:
            job.is_active = False
        
        self.db.commit()
        print(f"Marked {len(old_jobs)} old jobs as inactive")
    
    def _remove_old_inactive_jobs(self, days=30):
        """Remove inactive jobs older than the specified number of days"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted = self.db.query(Job).filter(
            Job.is_active == False,
            Job.updated_at < cutoff_date
        ).delete(synchronize_session=False)
        
        self.db.commit()
        print(f"Removed {deleted} old inactive jobs from the database")
    
    def schedule_sync(self, interval_hours=12):
        """Schedule periodic job sync"""
        schedule.every(interval_hours).hours.do(self.sync_jobs)
        
        # Run in background thread
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()
        
        return thread

# To use in main.py:
# from app.db.base import SessionLocal
# from app.services.job_sync import JobSyncService
# 
# # Start job sync on application startup
# @app.on_event("startup")
# def start_job_sync():
#     db = SessionLocal()
#     job_sync = JobSyncService(db)
#     job_sync.schedule_sync(interval_hours=12)

