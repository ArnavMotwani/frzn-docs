from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["health"])
async def health():
    """
    A simple liveness/readiness check.
    """
    return {"status": "ok"}