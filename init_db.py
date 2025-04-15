# Run this script once to initialize the database
from app.db.database import Base, engine
from app.models import User, Skill, Job, Application  # Import all your models

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()