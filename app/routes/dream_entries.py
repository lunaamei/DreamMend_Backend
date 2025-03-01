from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import DreamEntry, User, Summary
from app.schemas.dream_entries import DreamEntryCreate, DreamEntryResponse
from app.database import get_db
from app.security import get_current_user
from typing import List



router = APIRouter(
    tags=["dream_entries"]
)


@router.post("/migrate_summaries_to_dream_entries", response_model=List[DreamEntryResponse])
async def migrate_summaries_to_dream_entries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    summaries = db.query(Summary).filter(Summary.user_id == current_user.id, Summary.selected == True).all()
    
    if not summaries:
        print("No selected summaries found for migration")
        raise HTTPException(status_code=404, detail="No selected summaries found for migration")

    migrated_entries = []
    for summary in summaries:
        # Check if this summary has already been migrated
        existing_entry = db.query(DreamEntry).filter(DreamEntry.session_id == summary.session_id).first()
        if existing_entry:
            print(f"Summary with session_id: {summary.session_id} has already been migrated, skipping.")
            continue

        # Check if summary data is valid
        if not all([summary.title, summary.abstract, summary.original_dream, summary.rewritten_dream]):
            print(f"Invalid summary data for session_id: {summary.session_id}, skipping migration.")
            continue  # Skip this summary if any of the fields are None

        new_dream_entry = DreamEntry(
            user_id=summary.user_id,
            title=summary.title,
            abstract=summary.abstract,
            original_dream=summary.original_dream,
            rewritten_dream=summary.rewritten_dream,
            session_id=summary.session_id,
            created_date=summary.timestamp
        )
        
        db.add(new_dream_entry)
        migrated_entries.append(new_dream_entry)

    try:
        db.commit()
        for entry in migrated_entries:
            db.refresh(entry)
        print(f"Migrated {len(migrated_entries)} summaries to dream_entries")
    except Exception as e:
        db.rollback()
        print(f"Error during migration: {str(e)}")
        raise HTTPException(status_code=500, detail="Error during migration")

    return migrated_entries





@router.post("/dreamEntries", response_model=DreamEntryResponse)
async def create_dream_entry(
    dream_entry: DreamEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_dream_entry = DreamEntry(
        user_id=current_user.id,
        title=dream_entry.title,
        description=dream_entry.description,
        session_id=dream_entry.session_id
    )
    db.add(db_dream_entry)
    db.commit()
    db.refresh(db_dream_entry)
    return db_dream_entry

@router.get("/dreamEntries", response_model=List[DreamEntryResponse])
async def get_dream_entries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    entries = db.query(DreamEntry).filter(DreamEntry.user_id == current_user.id).all()
    
    
    for entry in entries:
        entry.abstract = entry.abstract or ""
        entry.original_dream = entry.original_dream or ""
        entry.rewritten_dream = entry.rewritten_dream or ""

        if "Are you happy with the generated summary? In this version of the application, you cannot modify the summary. The generated summary will be available to you on the IRT page. :)" in entry.rewritten_dream:
            entry.rewritten_dream = entry.rewritten_dream.replace("Are you happy with the generated summary? In this version of the application, you cannot modify the summary. The generated summary will be available to you on the IRT page. :)", "")
    
    return entries


    
   # entries = db.query(DreamEntry).filter(DreamEntry.user_id == current_user.id).all()
    #if not entries:
    #    print("No entries found")
   # return entries

@router.put("/dreamEntries/{entry_id}", response_model=DreamEntryResponse)
async def update_dream_entry(
    entry_id: int,
    dream_entry: DreamEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_dream_entry = db.query(DreamEntry).filter(DreamEntry.id == entry_id, DreamEntry.user_id == current_user.id).first()
    if not db_dream_entry:
        raise HTTPException(status_code=404, detail="Dream entry not found")
    
    db_dream_entry.title = dream_entry.title
    db_dream_entry.abstract = dream_entry.abstract
    db_dream_entry.original_dream = dream_entry.original_dream
    db_dream_entry.rewritten_dream = dream_entry.rewritten_dream
    db_dream_entry.times = dream_entry.times

    db.commit()
    db.refresh(db_dream_entry)
    return db_dream_entry

@router.delete("/dreamEntries/{entry_id}", response_model=DreamEntryResponse)
async def delete_dream_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_dream_entry = db.query(DreamEntry).filter(DreamEntry.id == entry_id, DreamEntry.user_id == current_user.id).first()
    if not db_dream_entry:
        raise HTTPException(status_code=404, detail="Dream entry not found")

    db.delete(db_dream_entry)
    db.commit()
    return db_dream_entry
