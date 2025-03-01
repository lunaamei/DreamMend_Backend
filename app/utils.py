from sqlalchemy.orm import Session
from .models import PasswordResetToken, EmailVerificationToken, User
from datetime import datetime, timedelta
import random
import string
import os
from mailersend.emails import NewEmail
from dotenv import load_dotenv
from .schemas import UserProfileUpdate 
import re

import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Retrieve API key and email sender address from environment variables
MAILERSEND_API_KEY = os.getenv("MAILERSEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")

# Function to generate a random 6-digit password reset token
def generate_password_reset_token():
    """
    Generate a random 6-digit token for password reset

    This function generates a 6-digit numeric token that will be used for password reset verification

    Returns:
        str:A 6-digit token as a string
    """
    token = ''.join(random.choices(string.digits, k=6))
    return token

# Function to save the password reset token in the database
def save_password_reset_token(user_id: int, token: str, db: Session):
    """
    Save the generated password reset token to the database

    This function creates a new PasswordResetToken instance with a 1-hour expiration time 
    and saves it to the database for the given user(I can make it for 30 minutes or less than that later)

    Args:
        user_id (int): The ID of the user requesting the password reset.
        token (str): The generated password reset token.
        db (Session): The database session used for the transaction.
    """

    # Set the expiration time for the token to 1 hour from now
    expires_at = datetime.utcnow() + timedelta(hours=1)
    # Create a new PasswordResetToken instance
    db_token = PasswordResetToken(user_id=user_id, token=token, expires_at=expires_at)
    # Add and commit the new token to the database
    db.add(db_token)
    db.commit()

# Function to send the password reset token via email
def send_password_reset_email(email: str, token: str):
    """
    Send the password reset token to the user's email

    This function sends an email containing the password reset token to the specified email address
    using the MailerSend API

    Args:
        email (str): The email address of the user.
        token (str): The password reset token to be included in the email.
    """

    # Initialize the MailerSend API client with the API key
    mailer = NewEmail(mailersend_api_key=MAILERSEND_API_KEY)
    # Load the HTML template
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inria+Sans:ital,wght@0,300;0,400;0,700;1,300;1,400;1,700&display=swap" rel="stylesheet">
        <title>Password Reset</title>
        <style>
            body {
                font-family: "Inria Sans", sans-serif;
                background-color: #3495C2;
                margin: 0;
                padding: 0;
            }
            .container {
                max-width: 600px;
                margin: 50px auto;
                background-color: #F5F5F5;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            .header {
                text-align: center;
                padding: 10px 0;
            }
            .header h1 {
                margin: 0;
                font-size: 24px;
                color: #383636;
            }

            .header p2 {
                margin: 0;
                font-size: 24px;
                color: #3495C2;
            }
            .content {
                margin: 20px 0;
            }
            .content p {
                font-size: 16px;
                color: #565656;
            }
            .content .token {
                display: block;
                width: fit-content;
                margin: 20px auto;
                padding: 10px 20px;
                background-color: #3495C2;
                color: #F6F6F6;
                border-radius: 4px;
                font-size: 20px;
                text-align: center;
            }
            .footer {
                text-align: center;
                padding: 10px 0;
                border-top: 1px solid #dddddd;
            }
            .footer p {
                font-size: 12px;
                color: #B5B5B5;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Unlocking your personal <p2>DreamMend<p2> </h1>
            </div>
            <div class="content">
                <p>Hello {{email}},</p>
                <p>You have requested to reset your password. Please use the following verification code to reset your password:</p>
                <div class="token">{{reset_token}}</div>
                <p>If you did not request a password reset, feel free to ignore this email.</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 DreamMend. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    # Replace placeholders in the template with actual values
    html_content = html_template.replace("{{email}}", email).replace("{{reset_token}}", token)

    #prepare the email data I added email instead of name on purpose later I will change it
    email_data = {
        "from": {
            "email": EMAIL_FROM,
            "name": "Dream-Mend"
        },
        "to": [
            {
                "email": email,
                "name": email
            }
        ],
        "subject": "Password Reset Token",
        "html": html_content,
        "text": f"Your password reset token is {token}"
    }

    
    try:
        # Send the email
        response = mailer.send(email_data)
        print("Email sent successfully")
    except Exception as e:
        # Handle any exceptions that occur during email sending
        print(f"Failed to send email: {str(e)}")



# Function to verify the password reset token
def verify_password_reset_token(token: str, db: Session):
    """
    Verify the password reset token

    This function checks if the provided token exists in the database and is not expired
    If valid, it returns the userID associated with the token; otherwise, it returns None

    Args:
        token (str):the password reset token to verify
        db (Session): The database session used for the query

    Returns:
        int or None: The userID if the token is valid, otherwise None
    """


    # Query the database for the token
    db_token = db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
    # Check if the token exists and is not expired
    if db_token and db_token.expires_at > datetime.utcnow():
        return db_token.user_id
    # Return None if the token is invalid or expired
    return None

##################### CHANGE EMAIL FUNCTIONALITY ###########################################

def generate_email_verification_token():
    """Generate a random 6-digit token for email verification"""
    token = ''.join(random.choices(string.digits, k=6))
    return token

def save_email_verification_token(user_id, new_email, token, db):
    verification_entry = EmailVerificationToken(
        user_id=user_id,
        new_email=new_email,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=1),  # 1-hour expiry
        is_used=False
    )
    db.add(verification_entry)
    db.commit()
    print(f"Verification Token: {token}")

"""def save_email_verification_token(user_id: int, new_email: str, token: str, db: Session):
    Save the email verification token and new email in the database
    # Set expiration time to 1 hour from now
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    # Create new EmailVerificationToken model instance
    db_token = EmailVerificationToken(
        user_id=user_id,
        new_email=new_email,
        token=token,
        expires_at=expires_at
    )
    
    db.add(db_token)
    db.commit()"""

def send_email_verification(email: str, token: str):
    """Send verification token to the new email address"""
    mailer = NewEmail(mailersend_api_key=MAILERSEND_API_KEY)
    
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Verification</title>
        <style>
            body {
                font-family: "Inria Sans", sans-serif;
                background-color: #3495C2;
                margin: 0;
                padding: 0;
            }
            .container {
                max-width: 600px;
                margin: 50px auto;
                background-color: #F5F5F5;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            .content .token {
                display: block;
                width: fit-content;
                margin: 20px auto;
                padding: 10px 20px;
                background-color: #3495C2;
                color: #F6F6F6;
                border-radius: 4px;
                font-size: 20px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                <h2>Verify Your New Email Address</h2>
                <p>Hello,</p>
                <p>Please use the following verification code to confirm your new email address:</p>
                <div class="token">{{verification_token}}</div>
                <p>If you did not request this change, please ignore this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    html_content = html_template.replace("{{verification_token}}", token)
    
    email_data = {
        "from": {
            "email": EMAIL_FROM,
            "name": "Dream-Mend"
        },
        "to": [
            {
                "email": email,
                "name": email
            }
        ],
        "subject": "Verify Your New Email Address",
        "html": html_content,
        "text": f"Your email verification code is: {token}"
    }
    
    try:
        response = mailer.send(email_data)
        logger.info("Email verification sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email verification: {str(e)}")
        raise

def verify_email_token(token: str, db: Session):
    """Verify the email verification token and return the associated data"""
    db_token = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == token,
        EmailVerificationToken.expires_at > datetime.utcnow(),
        EmailVerificationToken.is_used == False
    ).first()
    
    if db_token:
        return db_token
    return None


##################### FOR USERPROFILE ###########################################

def get_user_profile(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def update_user_profile(db: Session, user_id: int, profile_data: dict):
    # Retrieve user from database
    user = db.query(User).filter(User.id == user_id).first()

    print(profile_data, type(profile_data))  # Debug statement
    if not isinstance(profile_data, dict):
        raise ValueError("profile_data must be a dictionary")
    
    if user:
        
        # update user information
        for key, value in profile_data.items():
            setattr(user, key, value)
        # commit changes
        db.commit()
        db.refresh(user)
        return user
    return None

