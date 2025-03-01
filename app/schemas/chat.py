from pydantic import BaseModel
from datetime import datetime

# Schema for creating a new chat message
class ChatMessageCreate(BaseModel):
    conversation_id: str  # The unique identifier for the conversation this message belongs to
    session_id: str
    message: str  # The content of the message being sent
    is_from_user: bool  # a flag indicating whether the message is from the user(True) or the AI(False)
    #stage: str  #the stage of the conversation (e.g., "recording", "rewriting", etc.) 

class ChatMessageResponse(BaseModel):
    id: int  # The unique identifier of the chat message in the database
    conversation_id: str  # The unique identifier for the conversation this message belongs to
    session_id: str
    user_id: int  # The unique identifier of the user who sent/received the message
    message: str  # The content of the message
    is_from_user: bool  # a flag indicating whether the message is from the user (True) or the AI (False)
    timestamp: datetime  # The time when the message was created
    continueChat: bool  #A flag indicating whether the chat should continue or end
    is_active: bool  # A flag indicating whether the conversation is still active
    username: str  # The username of the user who sent/received the message
    #stage: str  # The stage of the conversation when this message was sent

    class Config:
        orm_mode = True # Enables compatibility with ORM models (SQLAlchemy)
