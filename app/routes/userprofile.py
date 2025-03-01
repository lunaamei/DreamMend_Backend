from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.userprofile import UserProfile, UserProfileUpdate, UserIDRequest
from app.models import User
from app.security import get_current_user
from app import utils

from fastapi import UploadFile, File, staticfiles
from ..main import UPLOAD_DIR  
from pathlib import Path
import shutil
import os
import uuid
 

# Initialize the FastAPI router with a tag for categorization
router = APIRouter(
    tags=["profile"]
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# ----------------- USER PROFILE ENDPOINTS -----------------

# Endpoint to retrieve the current user's profile information
@router.post("/profile", response_model=UserProfile)
def post_profile(current_user: User = Depends(get_current_user)):
    """
    Returns the currently authenticated user's profile information.

    Parameters:
    - current_user: The authenticated user (retrieved via dependency injection).

    Returns:
    - UserProfile: The user's profile details.
    """
    return current_user

# Endpoint to fetch user profile details from the database
@router.get("/profile", response_model=UserProfile)
def read_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Fetches the user's profile from the database.

    Parameters:
    - current_user: The authenticated user.
    - db: Database session.

    Returns:
    - UserProfile: The user's profile data if found, else raises a 404 error.
    """
    user_profile = utils.get_user_profile(db, user_id=current_user.id)
    if not user_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return user_profile

# ----------------- PROFILE UPDATE ENDPOINT -----------------

@router.patch("/profile", response_model=UserProfile)
def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates user profile information. If the email is changed, an email verification
    process is triggered before the update is finalized.

    Parameters:
    - profile_data: The updated profile data submitted by the user.
    - current_user: The authenticated user.
    - db: Database session.

    Returns:
    - UserProfile: The updated user profile.
    """
    profile_dict = dict(profile_data.model_dump(exclude_unset=True))
    
    # If the user is trying to change their email, initiate verification process
    if "email" in profile_dict and profile_dict["email"] != current_user.email:
        new_email = profile_dict["email"]
        
        # Generate and save verification token in the database
        token = utils.generate_email_verification_token()
        utils.save_email_verification_token(current_user.id, new_email, token, db)
        
        # Send a verification email to the new email address
        try:
            utils.send_email_verification(new_email, token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email"
            )
        
        # Remove email from profile update (email change requires verification)
        del profile_dict["email"]
        
        # Update any remaining profile fields
        if profile_dict:
            updated_profile = utils.update_user_profile(db, current_user.id, profile_dict)
            if not updated_profile:
                raise HTTPException(status_code=404, detail="Profile not found")
            
        return current_user
    
    # If no email change, update profile directly
    updated_profile = utils.update_user_profile(db, current_user.id, profile_dict)
    if not updated_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return updated_profile

# ----------------- EMAIL VERIFICATION ENDPOINT -----------------

@router.post("/verify-email")
def verify_email(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verifies the email change request using a token. If valid, updates the user's email.

    Parameters:
    - token: The verification token sent via email.
    - current_user: The authenticated user.
    - db: Database session.

    Returns:
    - Success message if the email update is completed.
    """
    verification = utils.verify_email_token(token, db)
    if not verification or verification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    try:
        # Update the user's email address
        user = db.query(User).filter(User.id == current_user.id).first()
        user.email = verification.new_email
        
        # Mark token as used
        verification.is_used = True
        
        db.commit()
        
        return {"message": "Email updated successfully"}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update email"
        )

# ----------------- PROFILE IMAGE UPLOAD ENDPOINT -----------------

@router.patch("/profile/image", response_model=UserProfile)
async def update_profile_image(
    profile_image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Allows users to upload and update their profile image.

    Parameters:
    - profile_image: The uploaded image file.
    - current_user: The authenticated user.
    - db: Database session.

    Returns:
    - UserProfile: The updated user profile with the new image URL.
    """
    # Allowed image extensions
    ALLOWED_EXTENSIONS = {"jpeg", "jpg", "png"}
    
    # Validate file type
    file_ext = profile_image.filename.split('.')[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content to validate file size (5MB max)
    contents = await profile_image.read()
    if len(contents) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size too large. Maximum size is 5MB."
        )
    await profile_image.seek(0)  # Reset file pointer

    try:
        # Generate a unique filename for the uploaded image
        filename = f"{current_user.id}_{uuid.uuid4()}.{file_ext}"
        file_path = UPLOAD_DIR / filename
        
        # Save the uploaded file to the server
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(profile_image.file, buffer)
        
        # Generate the public image URL
        image_url = f"/images/{filename}"
        
        # Retrieve user profile from the database
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Delete old profile image if it exists
        if user.profile_image_url:
            old_file = UPLOAD_DIR / user.profile_image_url.split('/')[-1]
            if old_file.exists():
                old_file.unlink()
        
        # Update the user's profile image URL in the database
        user.profile_image_url = image_url
        db.commit()
        db.refresh(user)
        
        return user
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image"
        )

