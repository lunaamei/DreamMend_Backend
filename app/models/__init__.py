"""
    Purpose: In FastAPI, the models directory typically contains your database models
    These models are defined using an ORM (Object-Relational Mapping) like SQLAlchemy
    The models represent the structure of our database tables, defining the fields, data types, 
    and relationships between different entities

    Usage: Models are crucial for interacting with the database
    They provide an abstraction layer that allows you to work with database records as Python objects 
    These models can then be used to perform CRUD (Create, Read, Update, Delete) operations on the database
"""
from .user import User, PasswordResetToken, EmailVerificationToken
from .chat import ChatMessage
from .summary import Summary
from .dream_entries import DreamEntry
