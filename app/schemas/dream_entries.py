from pydantic import BaseModel
from datetime import datetime

class DreamEntryCreate(BaseModel):
    title: str
    abstract: str
    original_dream: str
    rewritten_dream: str
    times: int = 0
    session_id: str

class DreamEntryResponse(DreamEntryCreate):
    id: int
    created_date: datetime

    class Config:
        orm_mode = True
