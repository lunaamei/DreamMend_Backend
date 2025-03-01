from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app import models, security, utils
from app.database import get_db
from app.schemas.auth import UserResponse, UserCreate, UserLogin, ForgotPassword, ResetPassword, CheckCode, TokenResponse, MessageResponse, ErrorResponse

# Initialize the router with a tag for organization
"""
Tags in FastAPI are used to group API routes for better organization and documentation
this tags=["auth"] definition in the APiRouter, is assigning the label "auth" to all the routes defined within that router
Why --> just for helping automatically generating well-organized API documentation

"""
router = APIRouter(
    tags=["auth"]
)

# Endpoint for user registration
@router.post("/signup", response_model=UserResponse, responses={400: {"model": ErrorResponse}})
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user in the web app (and store the information in db)

    This endpoint allows new users to sign up by providing a username, email, and password 
    The password is hashed before being stored in the database
    If the email is already registered, 
    an IntegrityError is raised, and a 400 Bad Request response is returned

    Args:
        user (UserCreate): The user creation schema containing username, email, and password
        db (Session):The database session dependency

    Returns:
        UserResponse: The newly created user object
    """
    # Hash the user's password
    hashed_password = security.get_password_hash(user.password)
    
    # Create a new user instance
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password,
    )
    try:
        # Add the new user to the database and commit the transaction
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        # Rollback the transaction if there is an IntegrityError(e.g., email already registered)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )



# Endpoint for user login
@router.post("/login", response_model=TokenResponse, responses={401: {"model": ErrorResponse}})
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return an access token

    This endpoint verifies the user's credentials (email and password), If the credentials are correct, 
    an access token is generated and returned
    If the credentials are invalid, a 401 Unauthorized response is returned

    Args:
        user (UserLogin): The user login schema containing email and password
        db (Session): The database session dependency

    Returns:
        TokenResponse: The access token and token type
    """

    # Fetch the user from the database based on email
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    
    # Verify the provided password against the stored hash
    if not db_user or not security.verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate an access token for the user
    access_token = security.create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}




# Endpoint to verify a token
@router.post("/verify-token", response_model=MessageResponse, responses={401: {"model": ErrorResponse}})
def verify_token(token: TokenResponse, db: Session = Depends(get_db)):
    """
    - Verify the validity of an access token

    This endpoint decodes the provided access token and checks if it corresponds to a valid user in the database
    If the token is valid, a message indicating success is returned 
    Otherwise, a 401 Unauthorized response is returned

    Args:
        token (TokenResponse): The access token to be verified
        db (Session): The database session dependency

    Returns:
        MessageResponse:a message indicating the token is valid
    """
    try:
        # Decode the access token
        payload = security.decode_access_token(token.access_token)
        email = payload.get("sub")
        
        # Verify the user exists in the database
        if email:
            db_user = db.query(models.User).filter(models.User.email == email).first()
            if db_user:
                return {"message": "Token is valid"}
    except Exception:
        pass
    
    # If the token is invalid or any error occurs, raise an unauthorized error
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")




# Endpoint to handle forgot password functionality
@router.post("/forgot-password", response_model=MessageResponse, responses={404: {"model": ErrorResponse}})
def forgot_password(email: ForgotPassword, db: Session = Depends(get_db)):
    """
    Initiate the password reset process for a user

    This endpoint generates a password reset token and sends it to the user's email 
    if the provided email is found in the system
    if the email is not registered, a 404 Not Found response is returned

    Args:
        email (ForgotPassword): The email of the user requesting the password reset
        db (Session): The database session dependency

    Returns:
        MessageResponse:a message indicating that the password reset link has been sent
    """

    # Fetch the user from the database based on email
    user = db.query(models.User).filter(models.User.email == email.email).first()
    
    # If the user is not found, raise a 404 error
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate a password reset token
    token = utils.generate_password_reset_token()
    
    # Save the reset token in the database and send an email to the user
    utils.save_password_reset_token(user.id, token, db)
    utils.send_password_reset_email(email.email, token)
    return {"message": "Password reset link sent"}




# Endpoint to check if the provided password reset code is valid
@router.post("/check-code", response_model=MessageResponse, responses={400: {"model": ErrorResponse}})
def check_code(data: CheckCode, db: Session = Depends(get_db)):
    """
    Verify the validity of a password reset token.

    This endpoint checks: 
    if the provided password reset token is valid and not expired
    if valid, a success message is returned 
    if the token is invalid or expired, a 400 Bad Request response is returned

    Args:
        data (CheckCode): The token to be verified
        db (Session):the database session dependency

    Returns:
        MessageResponse:a message indicating the token is valid
    """
    # Verify the password reset token
    user_id = utils.verify_password_reset_token(data.token, db)
    
    # If the token is invalid or expired, raise a 400 error
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"message": "Valid code"}




# Endpoint to reset the user's password
@router.post("/reset-password", response_model=MessageResponse, responses={400: {"model": ErrorResponse}})
def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    """
    reset a user's password using a valid password reset token

    This endpoint allows a user to reset their password by providing a valid reset token and a new password 
    if the token is valid, the user's password is updated 
    If the token is invalid or expired, a 400 Bad Request response is returned

    Args:
        data (ResetPassword): The reset password schema containing the token, new password, and confirmation
        db (Session): The database session dependency

    Returns:
        MessageResponse:a message indicating that the password has been reset successfully
    """

    # Check if the new password and confirmation match
    if data.new_password != data.new_password_confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    # Verify the password reset token
    user_id = utils.verify_password_reset_token(data.token, db)
    
    # If the token is invalid or expired, raise a 400 error
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Fetch the user from the database based on user_id
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    # If the user is not found, raise a 404 error
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update the user's password with the new hashed password
    user.password = security.get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password reset successfully"}
