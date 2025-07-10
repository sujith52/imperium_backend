from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Interaction
from sqlalchemy import func

router = APIRouter()

@router.get("/metrics/interactions-count")
def get_interactions_count(db: Session = Depends(get_db)):
    count = db.query(Interaction).count()
    return {"interactions_count": count}

@router.get("/metrics/active-users")
def get_active_users_count(db: Session = Depends(get_db)):
    active_users = db.query(Interaction.user_id).distinct().count()
    return {"active_users_count": active_users}

@router.get("/metrics/popular-items")
def get_popular_items(limit: int = 10, db: Session = Depends(get_db)):
    results = (
        db.query(Interaction.item_id, func.count(Interaction.item_id).label("count"))
        .group_by(Interaction.item_id)
        .order_by(func.count(Interaction.item_id).desc())
        .limit(limit)
        .all()
    )

    return {"popular_items": [{"item_id": item_id, "count": count} for item_id, count in results]}

@router.get("/metrics/cold-start-users")
def get_cold_start_users(threshold: int = 3, db: Session = Depends(get_db)):
    results = (
        db.query(Interaction.user_id)
        .group_by(Interaction.user_id)
        .having(func.count(Interaction.user_id) < threshold)
        .all()
    )

    cold_users = [user_id for (user_id,) in results]
    return {"cold_start_users": cold_users}
