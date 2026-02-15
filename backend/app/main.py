"""
FastAPI application entry point.
Configures the app, registers routes, and sets up error handling.
"""
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import tickets, feedback, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create app
app = FastAPI(
    title="LangGraph Support Agent",
    description="AI-powered customer support agent using LangGraph",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler to prevent 500 errors from leaking internal details.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred",
            "type": type(exc).__name__
        }
    )


# Register routers
app.include_router(health.router)
app.include_router(tickets.router)
app.include_router(feedback.router)


# Root endpoint
@app.get("/")
def root():
    """Root endpoint with API info."""
    return {
        "service": "LangGraph Support Agent",
        "status": "running",
        "docs": "/docs"
    }
