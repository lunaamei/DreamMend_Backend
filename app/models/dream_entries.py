from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship
from .user import Base

class DreamEntry(Base):
    """
    The DreamEntry model represents a dream entry created by the user.

    Attributes:
        id (int): Primary key, unique identifier for each dream entry.
        user_id (int): Foreign key referencing the ID of the user who created the entry.
        title (str): The title of the dream.
        description (str): The text content describing the dream.
        times (int): Number of times the dream has been rehearsed.
        created_date (datetime): The time when the dream entry was created, defaults to the current time.
        session_id (str): Identifier for the session to which this dream entry belongs.
    """

    __tablename__ = "dream_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    abstract = Column(Text, nullable=False)  
    original_dream = Column(Text, nullable=False)  
    rewritten_dream = Column(Text, nullable=False)  
    times = Column(Integer, default=0)
    created_date = Column(TIMESTAMP, server_default=func.now())
    session_id = Column(String, nullable=False)

    user = relationship("User", back_populates="dream_entries")
