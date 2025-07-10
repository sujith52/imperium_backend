from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import InteractionCreate, InteractionResponse, InteractionType
from app.models import Interaction, User, Item
from app.database import get_db
from fastapi import UploadFile, File
import csv
import io
from app.schemas import InteractionLogRequest
import csv
from datetime import datetime
from fastapi import UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import User, Item, Interaction
from app.database import get_db
from fastapi import APIRouter

from app.dependencies.auth import verify_api_key




router = APIRouter(prefix="/interactions", tags=["interactions"])

@router.post("/", response_model=InteractionResponse)
def log_interaction(interaction: InteractionCreate, db: Session = Depends(get_db)):
    # Check if user and item exist
    user = db.query(User).filter(User.id == interaction.user_id).first()
    item = db.query(Item).filter(Item.id == interaction.item_id).first()

    if not user or not item:
        raise HTTPException(status_code=404, detail="User or Item not found")

    db_interaction = Interaction(
        user_id=interaction.user_id,
        item_id=interaction.item_id,
        interaction_type=interaction.interaction_type,
        timestamp=datetime.utcnow()
    )
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

@router.get(
    "/",
    response_model=List[InteractionResponse],
    summary="Get Interactions with Pagination & Filters",
    description="Fetch interactions using filters like `user_id`, `item_id`, `interaction_type` with pagination.",
    responses={
        200: {"description": "Successful Response"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    }
)
def get_interactions(
    user_id: Optional[int] = None,
    item_id: Optional[int] = None,
    interaction_type: Optional[InteractionType] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Interaction)

    if user_id:
        query = query.filter(Interaction.user_id == user_id)
    if item_id:
        query = query.filter(Interaction.item_id == item_id)
    if interaction_type:
        query = query.filter(Interaction.interaction_type == interaction_type)

    return query.offset(skip).limit(limit).all()




router = APIRouter(prefix="/interactions", tags=["interactions"])

@router.post(
    "/upload_csv/",
    summary="Upload Interactions from CSV",
    description="Accepts a CSV file with user-item interactions. Creates users/items if they don’t exist.",
    responses={
        200: {"description": "CSV Uploaded Successfully"},
        400: {"description": "Bad Request - Invalid File Type"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    }
)
def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    contents = file.file.read().decode("utf-8").splitlines()
    reader = csv.DictReader(contents)

    added_count = 0
    for row in reader:
        username = row.get("user")
        movie_title = row.get("movie-title")
        rating = row.get("rating")
        genre = row.get("genre")

        if not username or not movie_title or not rating:
            continue

        # 1. Get or create user
        user = db.query(User).filter(User.name == username).first()
        if not user:
            user = User(name=username)
            db.add(user)
            db.commit()
            db.refresh(user)

        # 2. Get or create item (you may store genre if your model supports it)
        item = db.query(Item).filter(Item.name == movie_title).first()
        if not item:
            item = Item(name=movie_title)  # genre can be added here if your model supports it
            db.add(item)
            db.commit()
            db.refresh(item)

        # 3. Create interaction with rating
        interaction = Interaction(
            user_id=user.id,
            item_id=item.id,
            interaction_type=str(rating),  # Store rating as string or map it to something meaningful
            timestamp=datetime.utcnow()
        )
        db.add(interaction)
        added_count += 1

    db.commit()
    return {"message": f"{added_count} interactions uploaded successfully."}


from fastapi import status
from fastapi.responses import JSONResponse

@router.post(
    "/log/",
    response_model=InteractionResponse,
    status_code=201,
    summary="Log Real-time User Interaction",
    description="Records a real-time user interaction with an item.",
    responses={
        201: {"description": "Successful Response"},
        400: {"description": "Bad Request - Missing or invalid fields"},
        404: {"description": "User or Item not found"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    }
)
def log_interaction_realtime(
    interaction: InteractionLogRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == interaction.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    item = db.query(Item).filter(Item.id == interaction.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db_interaction = Interaction(
        user_id=interaction.user_id,
        item_id=interaction.item_id,
        interaction_type=interaction.interaction_type,
        timestamp=datetime.utcnow()
    )
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)

    return db_interaction
