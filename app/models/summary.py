from sqlalchemy import Column, Integer, ForeignKey, Text, Boolean, TIMESTAMP, func, String
from sqlalchemy.orm import relationship
from .user import Base


class Summary(Base):
    """
    The Summary model represents a summary of a conversation or content created by the user

    Attributes:
        id (int): Primary key, unique identifier for each summary
        user_id (int): Foreign key referencing the ID of the user who created the summary
        conversation_id (str): Identifier for the conversation to which this summary belongs
        session_id (str): Identifier for the session to which this summary belongs
        summary (str): The text content of the summary
        timestamp (datetime): The time when the summary was created, defaults to the current time
        selected (bool): a flag indicating whether this summary has been selected for some purpose, defaults to False

    Relationships:
        user (User):the user who created the summary, establishing a many-to-one relationship with the User model
    """

    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    conversation_id = Column(String, nullable=False)
    session_id = Column(String, nullable=False)  
    title = Column(String, nullable=False)  
    abstract = Column(String, nullable=False)  
    original_dream = Column(Text, nullable=False)  
    rewritten_dream = Column(Text, nullable=False)  
    selected = Column(Boolean, default=False) 
    timestamp = Column(TIMESTAMP, server_default=func.now())
     

    user = relationship("User", back_populates="summaries")