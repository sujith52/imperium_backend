from fastapi import FastAPI
from app.routes.user import router as user_router
from app.routes.item import router as item_router
from app.routes.interactions import router as interaction_router
from app.models import Base
from app.database import engine
from app.routes import interactions, recommendations
from app.routes import profiles
from app.routes import profiles, health
from app.middleware.logger import RequestLoggingMiddleware 
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="🎬 Movie Recommendation API",
    description="""
This API allows:

📌 Logging user-item interactions  
📌 Uploading CSV files of interactions  
📌 Generating movie recommendations  
📌 Health checks and user profiles

Built with ❤️ using FastAPI, SQLAlchemy, and Redis.
""",
    version="1.0.0",
    contact={
        "name": "imperium",
        "url": "https://your-portfolio-or-github-link.com",  # Optional
        "email": "sujit@example.com"  # Optional
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can change "*" to specific domains like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def root():
    return {"message": "Server is working!"}

# Include all route modules
app.include_router(user_router)
app.include_router(item_router)
app.include_router(interaction_router)
Base.metadata.create_all(bind=engine)
app.include_router(interactions.router)
app.include_router(recommendations.router)
app.include_router(profiles.router)
app.include_router(health.router)
app.add_middleware(RequestLoggingMiddleware)
Base.metadata.create_all(bind=engine)

