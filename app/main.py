from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import Base
from app.middleware.logger import RequestLoggingMiddleware

# Routers
from app.routes.user import router as user_router
from app.routes.item import router as item_router
from app.routes.interactions import router as interaction_router
from app.routes.interactions import router as interactions_router
from app.routes.recommendations import router as recommendations_router
from app.routes.profiles import router as profiles_router
from app.routes.health import router as health_router
from app.routes.metrics import router as metrics_router
from app.admin_routes import router as admin_router

# App init
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
        "name": "Imperium",
        "url": "https://your-portfolio-or-github-link.com",
        "email": "sujit@example.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

# Root route
@app.get("/")
def root():
    return {"message": "Server is working!"}

# DB setup (once only)
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(user_router)
app.include_router(item_router)
app.include_router(interaction_router)
app.include_router(interactions_router)
app.include_router(recommendations_router)
app.include_router(profiles_router)
app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(admin_router)
