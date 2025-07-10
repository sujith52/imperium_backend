from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Replace 'your_password' with your actual PostgreSQL password
DATABASE_URL = "postgresql://postgres:postgres@localhost/recommend_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# ✅ Add this to app/database.py if not already there


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
