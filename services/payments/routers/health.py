from fastapi import APIRouter
from sqlalchemy import text
from database import engine

router = APIRouter()


@router.get("/")
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "service": "payments"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503

