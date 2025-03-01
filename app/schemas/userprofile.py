from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

# this was for testing and it worked - maybe theres incoherence with id <=> user_id
class UserIDRequest(BaseModel):
    user_id: int

class UserProfile(BaseModel):
    id: int
    header_image_url: Optional[str] = None
    profile_image_url: Optional[str] = None
    name: Optional[str] = None
    email: EmailStr
    surname: Optional[str] = None
    date_of_birth: Optional[date] = None
    username: str
    phone_number: Optional[str] = None
    gender: Optional[str] = None  # new field
    region: Optional[str] = None  # new field
    education: Optional[str] = None  # new field

    class Config:
        from_attributes = True
        #orm_mode = True



class UserProfileUpdate(BaseModel):
    header_image_url: Optional[str] = None
    profile_image_url: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    surname: Optional[str] = None
    date_of_birth: Optional[date] = None
    username: Optional[str] = None
    phone_number: Optional[str] = None
    gender: Optional[str] = None  # new field
    region: Optional[str] = None  # new field
    education: Optional[str] = None  # new field
    

    class Config:
        from_attributes = True
        #orm_mode = True
