from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import sys
import os
from pathlib import Path
import shutil
import uuid

# Create a directory for storing images that persists outside Docker
UPLOAD_DIR = Path("/app/data/profile_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../AI')))

from app.routes import auth, chat as chat_routes
from app.database import engine, Base
from app.routes import summary 
from app.routes import userprofile, home #added for userprofile
from app.routes import dream_entries


# Initialize the FastAPI application
app = FastAPI()

# Configure CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Create all tables in the database
Base.metadata.create_all(bind=engine)


# Include the authentication and chat routers
app.include_router(auth.router)
app.include_router(chat_routes.router)
app.include_router(userprofile.router )#added for userprofile
app.include_router(home.router )#added for home
app.include_router(summary.router)  
app.include_router(dream_entries.router)



# Serve files from the /app/data/profile_images directory
app.mount("/images", StaticFiles(directory=str(UPLOAD_DIR)), name="images")


# Entry point for running the application
if __name__ == "__main__":
    import uvicorn
    #uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

