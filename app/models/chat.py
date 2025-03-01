from sqlalchemy import Column, Integer, ForeignKey, Text, Boolean, TIMESTAMP, func, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .user import Base


class ChatMessage(Base):
    """
    The ChatMessage model represents a message within a chat conversation

    Attributes:
        id (int): Primary key, unique identifier for each chat message
        user_id (int): Foreign key referencing the ID of the user who sent the message
        conversation_id (str): identifier for the conversation to which this message belongs
        message (str): The text content of the chat message
        is_from_user (bool): Indicates whether the message was sent by the user(True) or received from the system (False)
        timestamp (datetime):The time when the message was created, defaults to the current time
        is_active (bool): A flag indicating whether the conversation is still active, defaults to True
        stage (str):represents the stage of the conversation, useful for tracking the progress of the conversation
        
    Relationships:
        user (User): The user who sent the message, establishing a many-to-one relationship with the User model
    """

    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    conversation_id = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_from_user = Column(Boolean, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    is_active = Column(Boolean, default=True)  
   # stage = Column(String)  # Add a default stage to add different stages in database
    user = relationship("User", back_populates="messages")

# Make sure this relationship definition is correct and in only one place -> if you want to test it
# User.messages = relationship("ChatMessage", order_by=ChatMessage.id, back_populates="user")



