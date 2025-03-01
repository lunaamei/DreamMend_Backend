from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from . import models, database
import os


# Initialize the password context for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Load secret key and algorithm from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# OAuth2 password bearer token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Function to hash a password
def get_password_hash(password: str) -> str:
    """
    Hashes a plain text password using the bcrypt algorithm
    
    Args:
        password (str):the plain text password to hash

    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)



# Function to verify a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that a plain text password matches a hashed password
    
    Args:
        plain_password (str):the plain text password
        hashed_password (str): The hashed password to compare against

    Returns:
        bool: True if the passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)



# Function to create an access token
def create_access_token(data: dict) -> str:
    """
    Creates a new JWT access token
    
    Args:
        data (dict): The data to include in the JWT payload

    Returns:
        str: The encoded JWt access token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



# Function to decode an access token
def decode_access_token(token: str):
    """
    decodes a JWT access token
    
    Args:
        token (str): The JWT token to decode

    Returns:
        dict: The decoded payload from the token

    Raises:
        HTTPException: If the token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

"""
# Dependency function to get the current user based on the token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
"""

# Testing function with email instead of Id since the email is also unique and I will add more explanation later ~,~
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """
    Retrieves the current authenticated user based on the JWT token
    
    This function decodes the JWT token to extract the user's email and retrieves the user from the database 
    If the token is invalid or the user is not found, 
    an HTTP 401 Unauthorized exception is raised

    Args:
        token (str): The JWT token used for authentication
        db (Session): The database session dependency

    Returns:
        User: The authenticated user

    Raises:
        HTTPException: If the token is invalid or the user cannot be found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        print(f"Payload: {payload}")  # Debug print
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError as e:
        print(f"JWTError: {e}")  # Debug print
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
