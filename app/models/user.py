from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Date, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship, declarative_base



# Base class for our ORM models
Base = declarative_base()

class User(Base):
    """
    The User model represents a user in the application

    Attributes:
        id (int): primary key, unique identifier for each user
        username (str): The username of the user, cannot be null
        email (str): The email of the user, must be unique and cannot be null
        password (str): The hashed password of the user, cannot be null
        header_image_url (str, optional): URL of the user's header image
        profile_image_url (str, optional): URL of the user's profile image
        name (str, optional): The first name of the user
        surname (str, optional): The surname of the user
        date_of_birth (date, optional): The date of birth of the user
        phone_number (str, optional): The phone number of the user
        created_at (datetime):Timestamp when the user was created, defaults to current time
        updated_at (datetime): Timestamp when the user was last updated, updates to current time on each update

    Relationships:
        messages (ChatMessage):List of messages associated with the user, establishing a one-to-many relationship
        summaries (Summary):List of summaries associated with the user, establishing a one-to-many relationship
    """

    __tablename__ = "users"  # Table name in the database

    id = Column(Integer, primary_key=True, index=True)  # Primary key, unique identifier for each user
    username = Column(String(255), nullable=False)  # Username of the user, cannot be null
    email = Column(String(255), unique=True, nullable=False)  # Email of the user, must be unique and cannot be null
    password = Column(String(255), nullable=False)  # Hashed password of the user, cannot be null
    ################ added for userprofile
    header_image_url = Column(String, nullable=True)  
    profile_image_url = Column(String, nullable=True)
    name = Column(String(255), nullable=True)
    surname = Column(String(255), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    phone_number = Column(String(255), nullable=True)
    ################
    gender = Column(String(255), nullable=True)
    region = Column(String(255), nullable=True)
    education = Column(String(255), nullable=True)
    ################
    created_at = Column(TIMESTAMP, server_default=func.now())  # Timestamp when the user was created, defaults to current time
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())  # Timestamp when the user was last updated, updates to current time on each update
    messages = relationship("ChatMessage", back_populates="user")
    summaries = relationship("Summary", back_populates="user")
    dream_entries = relationship("DreamEntry", back_populates="user")

class PasswordResetToken(Base):
    """
    The PasswordResetToken model represents a token used for resetting a user's password

    Attributes:
        id (int): Primary key, unique identifier for each token
        user_id (int):foreign key referencing the ID of the user to whom the token belongs
        token (str): The password reset token
        expires_at (datetime): The timestamp when the token expires
        created_at (datetime): The timestamp when the token was created, defaults to the current time
    """

    __tablename__ = "password_reset_tokens"  # Table name in the database

    id = Column(Integer, primary_key=True, index=True)  # Primary key, unique identifier for each token
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Foreign key referencing the user's ID, cannot be null
    token = Column(String(255), nullable=False)  # The password reset token, cannot be null
    expires_at = Column(TIMESTAMP, nullable=False)  # Timestamp when the token expires, cannot be null
    created_at = Column(TIMESTAMP, server_default=func.now())  # Timestamp when the token was created, defaults to current time


# model for email verification tokens
class EmailVerificationToken(Base):

    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, index=True)  # Primary key, unique identifier for each token
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Foreign key referencing the user's ID, cannot be null
    new_email = Column(String(255), nullable=False)  # The new email address to be verified, cannot be null
    token = Column(String(255), nullable=False)  # The password reset token, cannot be null
    expires_at = Column(TIMESTAMP, nullable=False)  # Timestamp when the token expires, cannot be null
    created_at = Column(TIMESTAMP, server_default=func.now())  # Timestamp when the token was created, defaults to current time
    is_used = Column(Boolean, nullable=False, default=False)  # Flag to indicate if the token has been used

