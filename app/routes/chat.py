from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from app.models import ChatMessage, User, Summary
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse
from app.schemas.summary import SummaryCreate, SummaryResponse
from app.routes.summary import create_summary
from app.database import get_db
from app.security import get_current_user
import logging
import sys
import os
from datetime import datetime
import uuid
from io import StringIO
#from app.utils import parse_summary
from app.routes.dream_entries import migrate_summaries_to_dream_entries
#from app.routes.irt_app import full_chain


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../AI')))


from irt_app import full_chain

logger = logging.getLogger(__name__)

# Initialize the router with a tag for organization
router = APIRouter(
    tags=["chat"]
)

@router.post("/conversations", response_model=dict)
async def create_conversation(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Create a new conversation session

    This endpoint generates a unique conversationID to start a new conversation session
    The ID can be used to track the conversation's progress

    Args:
        current_user (User): The current logged-in user, fetched using dependency injection
        db (Session): The database session dependency

    Returns:
        str: The unique conversationID
    """
  
    conversation_id = str(uuid.uuid4())  # generates a unique identifier for a new conversation session
    session_id = str(uuid.uuid4())  # Generates a unique session_id
    
    return {"conversation_id": conversation_id, "session_id": session_id}

@router.post("/messages", response_model=ChatMessageResponse)
async def send_message(
    message: ChatMessageCreate,
    conversation_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not message.session_id:
        raise HTTPException(status_code=400, detail="Session ID cannot be null")

    """
    Send a message in an active conversation and receive an AI generated response

    This endpoint handles sending user messages during an ongoing conversation
    It checks the current stage of the conversation, processes the user's message, and generates a response using an AI model
    The conversation stage is then updated accordingly

    Args:
        message (ChatMessageCreate): The user's message to be sent
        conversation_id (str): The ID of the conversation
        request (Request): The incoming HTTP request
        current_user (User): the current logged-in user, fetched using dependency injection
        db (Session): The database session dependency

    Returns:
        ChatMessageResponse: The AI generated response and updated conversation details
    """

    logger.info(f"Received payload: {message.json()}")  # Log received data

    # Check if the conversation is active
    last_message = db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conversation_id,
        ChatMessage.session_id == message.session_id 
    ).order_by(ChatMessage.timestamp.desc()).first()
    if last_message and not last_message.is_active:
        raise HTTPException(status_code=400, detail="The chat has been ended.")

    # Save the user's message
    db_message = ChatMessage(
        user_id=current_user.id,
        conversation_id=conversation_id,
        session_id=message.session_id,
        message=message.message,
        is_from_user=True,
        is_active=True,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    logger.info(f"Received message from user {current_user.id}: {message.message}")

    try:
        response = full_chain.invoke(
            {"input": message.message},
            {"configurable": {
                "conversation_id": conversation_id,
                "user_id": current_user.id,
                "session_id": message.session_id  
            }}
        )

        logger.info(f"AI response structure: {response}")

        # Handle AI response
        if isinstance(response, str):
            ai_message = response
            is_finished = any(ending in ai_message.lower() for ending in ["goodbye", "bye"])
        elif isinstance(response, dict) and 'response' in response:
            ai_message = response['response']
            is_finished = response.get('is_finished', False) or any(ending in ai_message.lower() for ending in ["goodbye", "bye"])

        # Initialize variables for storing summary parts
        title = None
        abstract = None
        original_dream = None
        rewritten_dream = None

        # Extract and store each part of the summary
        if "Title:" in ai_message:
            title = ai_message.split("Title:")[1].split("Abstract:")[0].strip()

        if "Abstract:" in ai_message:
            abstract = ai_message.split("Abstract:")[1].split("Original Dream:")[0].strip()

        if "Original Dream:" in ai_message:
            original_dream = ai_message.split("Original Dream:")[1].split("Rewritten Dream:")[0].strip()

        if "Rewritten Dream:" in ai_message:
            rewritten_dream = ai_message.split("Rewritten Dream:")[1].strip()

        # Create a new Summary record if all parts are present
        if title and abstract and original_dream and rewritten_dream:
            summary_data = SummaryCreate(
                conversation_id=conversation_id,
                session_id=message.session_id,
                title=title,
                abstract=abstract,
                original_dream=original_dream,
                rewritten_dream=rewritten_dream,
                user_id=current_user.id  
            )
            # Store the Summary in the database
            summary_response = await create_summary(summary_data, db)

            if not summary_response:
                raise HTTPException(status_code=500, detail="Failed to create summary")
            
            await migrate_summaries_to_dream_entries(db=db, current_user=current_user)
        # Save AI response message
        db_ai_message = ChatMessage(
            user_id=current_user.id,
            conversation_id=conversation_id,
            session_id=message.session_id,
            message=ai_message,
            is_from_user=False,
            is_active=not is_finished,
        )
        db.add(db_ai_message)
        db.commit()
        db.refresh(db_ai_message)

        return ChatMessageResponse(
            id=db_ai_message.id,
            user_id=db_ai_message.user_id,
            message=db_ai_message.message,
            is_from_user=db_ai_message.is_from_user,
            timestamp=db_ai_message.timestamp,
            continueChat=not is_finished,
            conversation_id=conversation_id,
            session_id=message.session_id,
            is_active=not is_finished,
            username=current_user.username,
        )

    except Exception as e:
        logger.error(f"AI service error: {str(e)}")
        raise HTTPException(status_code=500, detail="AI service error")

                
@router.get("/export_chat/{conversation_id}", response_class=FileResponse)
async def export_chat(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export chat history for a specific conversation as a text file.

    Args:
        conversation_id (str): The ID of the conversation to export.
        current_user (User): The current logged-in user.
        db (Session): The database session dependency.

    Returns:
        FileResponse: The generated text file containing chat history.
    """
    # Retrieve chat messages for the given conversation ID
    messages = db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conversation_id,
        ChatMessage.user_id == current_user.id
    ).order_by(ChatMessage.timestamp.asc()).all()

    if not messages:
        raise HTTPException(status_code=404, detail="No messages found for the given conversation ID.")

    # Prepare the chat history as a text file
    chat_history = StringIO()
    for message in messages:
        sender = "You" if message.is_from_user else "AI"
        chat_history.write(f"[{message.timestamp}] {sender}: {message.message}\n")

    # Create a temporary file to store chat history
    file_path = f"/tmp/chat_history_{conversation_id}.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(chat_history.getvalue())

    return FileResponse(file_path, filename=f"chat_history_{conversation_id}.txt")                    
                    
