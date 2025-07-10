from fastapi import APIRouter, HTTPException, Depends
from fastapi import Query
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models import User, Item, Interaction
from app.database import get_db
from app.redis_client import redis_client

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

# Schema
class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[int]

import logging

@router.get("/{user_id}", response_model=List[str])
def get_recommendations(
    user_id: int,
    limit: int = Query(5, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    try:
        logging.info(f"Looking for cache for user {user_id}")
        cache_key = f"user:{user_id}:recommendations"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            logging.info("Found in cache")
            return cached_data.split(",")

        logging.info("Not found in cache, checking DB")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logging.warning("User not found")
            raise HTTPException(status_code=404, detail="User not found")

        interacted = db.query(Interaction.item_id).filter(Interaction.user_id == user_id).subquery()
        new_items = db.query(Item).filter(~Item.id.in_(interacted)).limit(limit).offset(offset).all()

        recommendations = [item.name for item in new_items]
        logging.info(f"Recommendations: {recommendations}")

        redis_client.setex(cache_key, 3600, ",".join(recommendations))
        return recommendations

    except Exception as e:
        logging.exception("Something went wrong in get_recommendations")
        raise HTTPException(status_code=500, detail=str(e))
