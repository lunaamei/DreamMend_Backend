# This file can be left empty or used to import and re-export schemas
# for easier imports in other parts of the application if needed?
from .userprofile import UserProfile, UserProfileUpdate 


"""
    Purpose: In FastAPI, the schemas directory is where you define Pydantic models, which are used for data validation, serialization, and deserialization 
    These schemas define the structure of the data that our APIs will accept in requests and send in responses

--> Pydantic models help ensure that data adheres to the expected format and types
    Usage: Schemas are used to validate and serialize data in FastAPI. 

"""