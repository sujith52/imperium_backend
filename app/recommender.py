from sqlalchemy.orm import Session
from app.models import Interaction, Item

def get_top_recommendations(user_id: int, db: Session, limit: int = 5):
    # Get item IDs the user has already interacted with
    interacted = db.query(Interaction.item_id).filter(Interaction.user_id == user_id).distinct()
    interacted_ids = [i.item_id for i in interacted]

    # Recommend items not yet interacted with
    new_items = db.query(Item).filter(~Item.id.in_(interacted_ids)).limit(limit).all()
    return [item.name for item in new_items]
