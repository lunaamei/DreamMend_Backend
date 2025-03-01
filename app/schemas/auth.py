from pydantic import BaseModel, EmailStr

# Schema for creating a new user
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Schema for user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schema for forgot password request
class ForgotPassword(BaseModel):
    email: EmailStr

# Schema for checking the reset code/token
class CheckCode(BaseModel):
    token: str

# Schema for resetting the password
class ResetPassword(BaseModel):
    token: str
    new_password: str
    new_password_confirm: str

# Schema for the user response
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    # Configuration to support ORM mode
    class Config:
        orm_mode = True

# Schema for the token response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# Schema for a simple message response
class MessageResponse(BaseModel):
    message: str

# Schema for an error response
class ErrorResponse(BaseModel):
    detail: str
