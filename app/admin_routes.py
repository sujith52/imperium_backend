from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import get_db
from app.models import User, Item, Interaction
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin/metrics", tags=["Admin Metrics"])

@router.get("/summary")
async def get_metrics_summary(db: Session = Depends(get_db)):
    # Total counts
    total_users = db.query(func.count(User.id)).scalar()
    total_items = db.query(func.count(Item.id)).scalar()
    total_interactions = db.query(func.count(Interaction.id)).scalar()

    # Active users in the last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    active_users = db.query(func.count(func.distinct(Interaction.user_id))).filter(Interaction.timestamp >= seven_days_ago).scalar()

    # Top 5 items by interaction count
    top_items_data = (
        db.query(Item.name, func.count(Interaction.id).label("interaction_count"))
        .join(Interaction, Interaction.item_id == Item.id)
        .group_by(Item.id)
        .order_by(desc("interaction_count"))
        .limit(5)
        .all()
    )
    top_items = [{"item_title": row.name, "count": row.interaction_count} for row in top_items_data]


    return {
        "total_users": total_users,
        "total_items": total_items,
        "total_interactions": total_interactions,
        "active_users_last_7_days": active_users,
        "top_items": top_items
    }

from sqlalchemy import cast, Date

@router.get("/interactions-daily")
async def get_daily_interactions(db: Session = Depends(get_db)):
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    results = (
        db.query(
            cast(Interaction.timestamp, Date).label("date"),
            func.count().label("count")
        )
        .filter(Interaction.timestamp >= seven_days_ago)
        .group_by(cast(Interaction.timestamp, Date))
        .order_by(cast(Interaction.timestamp, Date))
        .all()
    )

    return [{"date": str(row.date), "count": row.count} for row in results]

@router.get("/top-active-users")
async def get_top_active_users(db: Session = Depends(get_db)):
    results = (
        db.query(
            User.name,
            func.count(Interaction.id).label("interaction_count")
        )
        .join(Interaction, User.id == Interaction.user_id)
        .group_by(User.id)
        .order_by(desc("interaction_count"))
        .limit(5)
        .all()
    )

    return [{"user_name": row.name, "count": row.interaction_count} for row in results]

@router.get("/interactions-hourly")
async def get_hourly_interactions(db: Session = Depends(get_db)):
    one_day_ago = datetime.utcnow() - timedelta(hours=24)

    results = (
        db.query(
            func.date_trunc('hour', Interaction.timestamp).label('hour'),
            func.count(Interaction.id).label('count')
        )
        .filter(Interaction.timestamp >= one_day_ago)
        .group_by(func.date_trunc('hour', Interaction.timestamp))
        .order_by('hour')
        .all()
    )

    return [
        {"hour": row.hour.strftime("%Y-%m-%d %H:%M:%S"), "count": row.count}
        for row in results
    ]
