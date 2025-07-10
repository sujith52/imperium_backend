from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/", summary="Health Check", description="Returns OK if the service is running.")
def health_check():
    return {"status": "OK"}
