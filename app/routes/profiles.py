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




@router.get("/profiles/users/{user_id}")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    users = db.query(User).all()
    print("✅ Users in DB:", users)

    print("🔍 Looking for user_id:", user_id)
    user = db.query(User).filter(User.id == user_id).first()
    print("🧾 User found:", user)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/profiles/items/{item_id}")
def get_item_profile(item_id: int, db: Session = Depends(get_db)):
    items = db.query(Item).all()
    print("✅ Items in DB:", items)

    print("🔍 Looking for item_id:", item_id)
    item = db.query(Item).filter(Item.id == item_id).first()
    print("🧾 Item found:", item)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


