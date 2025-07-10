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

@router.get(
    "/{user_id}",
    response_model=List[str],
    summary="Get Recommendations for a User",
    description="Fetches item recommendations for a given user using basic logic or Redis cache.",
    responses={
        200: {"description": "Successful Response"},
        404: {"description": "User not found"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    }
)
def get_recommendations(
    user_id: int,
    limit: int = Query(5, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    # ✅ Check if recommendations are cached
    cache_key = f"user:{user_id}:recommendations"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        # If found in Redis, return cached list
        return cached_data.split(",")

    # ✅ Not cached: proceed with DB logic
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get items NOT yet interacted with
    interacted = db.query(Interaction.item_id).filter(Interaction.user_id == user_id).subquery()
    new_items = db.query(Item).filter(~Item.id.in_(interacted)).limit(5).all()

    recommendations = [item.name for item in new_items]

    # ✅ Save to Redis for future requests (cached for 1 hour = 3600 seconds)
    redis_client.setex(cache_key, 3600, ",".join(recommendations))

    return recommendations