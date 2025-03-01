from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Summary
from app.schemas.summary import SummaryCreate, SummaryResponse
from app.database import get_db
from datetime import datetime
from app.routes.dream_entries import migrate_summaries_to_dream_entries
#from app.utils import parse_summary 

import logging


# Initialize the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Initialize the router with a tag for organization
router = APIRouter(
    tags=["summary"]  
)

@router.post("/summary", response_model=SummaryResponse)
async def create_summary(
    summary: SummaryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new summary for a specific conversation.

    This endpoint allows users(AI will generate the summary and it will store in db wih this code :) but I didn't know how should I explain it) to create a summary of a conversation 
    The summary is stored in the database with a reference to the user and conversationIDs

    Args:
        summary (SummaryCreate): The summary creation schema containing the summary text, userID, and conversationID
        db (Session): The database session dependency

    Returns:
        SummaryResponse: The newly created summary object
    """
    # Validate the presence of all required fields
    if not all([summary.title, summary.abstract, summary.original_dream, summary.rewritten_dream]):
        raise HTTPException(status_code=400, detail="Incomplete summary data")

    # Create a new summary instance
    db_summary = Summary(
        user_id=summary.user_id,  # Set the user ID
        conversation_id=summary.conversation_id,  # Set the conversation ID
        session_id=summary.session_id,
        title=summary.title,
        abstract=summary.abstract,
        original_dream=summary.original_dream,
        rewritten_dream=summary.rewritten_dream,
        selected=True,
        timestamp=datetime.utcnow()  # Set the timestamp to the current UTC time
    )
    try:
        db.add(db_summary)
        db.commit()
        db.refresh(db_summary)
        logger.info(f"Summary successfully saved: {db_summary}")
    except Exception as e:
        logger.error(f"Error saving summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Summary could not be saved")

    return db_summary

@router.post("/summary/select/{summary_id}", response_model=SummaryResponse)
async def select_summary(
    summary_id: int,
    db: Session = Depends(get_db)
):
    """
    Select a specific summary as the chosen summary for a conversation

    This endpoint marks a specific summary as selected, 
    while unselecting any other summaries for the same conversation

    Args:
        summary_id (int): The ID of the summary to be selected
        db (Session): The database session dependency

    Returns:
        SummaryResponse: The selected summary object
    """
    # Find the summary to be selected
    db_summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not db_summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    # Unselect other summaries for the same conversation
    db.query(Summary).filter(Summary.conversation_id == db_summary.conversation_id).update({Summary.selected: False})

    # Select the specified summary
    db_summary.selected = True
    db.commit()
    db.refresh(db_summary)

    # 
    await migrate_summaries_to_dream_entries(db=db, current_user=db_summary.user)

    # Return the selected summary as a response
    return db_summary
