from pydantic import BaseModel
from datetime import datetime

# Schema for creating a new summary
class SummaryCreate(BaseModel):
    conversation_id: str  # he unique identifier for the conversation this summary belongs to
    session_id: str
    user_id: int  #the unique identifier of the user who created the summary
    title: str  
    abstract: str  
    original_dream: str  
    rewritten_dream: str  


# Schema for responding with a summary
class SummaryResponse(BaseModel):
    id: int  #the unique identifier of the summary in the database
    user_id: int  #the unique identifier of the user who created the summary
    conversation_id: str  # The unique identifier for the conversation this summary belongs to
    session_id: str
    title: str
    abstract: str
    original_dream: str
    rewritten_dream: str
    selected: bool  # A flag indicating whether this summary has been selected as the final one
    timestamp: datetime  #The time when the summary was created
    

    class Config:
        orm_mode = True  # Enables compatibility with ORM models(SQLAlchemy)
