from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()  

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Create a new SQLAlchemy engine instance
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for the models to inherit from
Base = declarative_base()

# Dependency function to get the database session
def get_db():
    """
    dependency function to create a new database session for a request
    
    This function provides a new database session for each request by yielding a 
    session from the SessionLocal factory.the session is closed once the request 
    is complete, ensuring proper resource management

    Yields:
        db (Session): A new database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
