"""
Health check API route.
"""
from fastapi import APIRouter
from app.schemas.response import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Check if the service is running."""
    return HealthResponse(
        status="ok",
        service="langgraph-support-agent"
    )
