from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Interaction, Item
from app.schemas import ProfileResponse
from app.recommender import get_top_recommendations

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.get("/users/{user_id}", response_model=ProfileResponse, summary="Get User Profile")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    # 1. Get user info
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Get interaction stats
    interactions = db.query(Interaction).filter(Interaction.user_id == user_id).all()
    total_interactions = len(interactions)
    unique_items = len(set(i.item_id for i in interactions))

    # 3. Get top 5 recommendations
    recommendations = get_top_recommendations(user_id, db)  # returns List[str]

    # 4. Return all info
    return {
        "user_id": user.id,
        "user_name": user.name,
        "total_interactions": total_interactions,
        "unique_items_viewed": unique_items,
        "recommendations": recommendations
    }


@router.get("/items/{item_id}", summary="Get Item Profile")
def get_item_profile(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item.id, "name": item.name}
