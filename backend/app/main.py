
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import PROJECT_NAME, VERSION
from app.database import Base, engine

from app.models.memory import Memory
from app.models.agent import Agent
from app.models.agent_credential import AgentCredential
from app.models.agent_message import AgentMessage

from app.core.agent_security import get_current_agent

# API imports
from app.api.memory import router as memory_router
from app.api.graph import router as graph_router
from app.api.patterns import router as patterns_router
from app.api.hypotheses import router as hypotheses_router
from app.api.discovery import router as discovery_router
from app.api.connections import router as connections_router
from app.api.semantic import router as semantic_router
from app.api.validator import router as validator_router

from app.api.advanced_discovery import (
    router as advanced_discovery_router
)

from app.api.reasoning import router as reasoning_router

from app.api.advanced_reasoning import (
    router as advanced_reasoning_router
)

from app.api.agent import router as agent_router
from app.api.agent_communication import (
    router as agent_communication_router
)

# Create database tables
Base.metadata.create_all(bind=engine)


# Initialize FastAPI
app = FastAPI(
    title=PROJECT_NAME,
    description="Your personal AI-powered cognitive assistant",
    version=VERSION
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "message": (
                "An unexpected error occurred. "
                "Please try again later."
            ),
            "path": request.url.path
        }
    )


# Register API routers
app.include_router(memory_router)
app.include_router(graph_router)
app.include_router(patterns_router)
app.include_router(hypotheses_router)
app.include_router(discovery_router)
app.include_router(connections_router)
app.include_router(semantic_router)
app.include_router(validator_router)
app.include_router(advanced_discovery_router)
app.include_router(reasoning_router)
app.include_router(advanced_reasoning_router)
app.include_router(agent_router)
app.include_router(agent_communication_router)

# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to Second Mind API!",
        "status": "running"
    }


# Server health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# Database readiness check
@app.get("/ready")
def readiness_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "database": "connected"
        }

    except Exception:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "database": "unavailable"
            }
        )


# Authenticated agent identity endpoint
@app.get(
    "/agent/me",
    tags=["Agent Authentication"],
    summary="Get Current Agent Identity"
)
def get_agent_identity(
    current_agent: Agent = Depends(get_current_agent)
):
    return {
        "status": "authenticated",
        "agent_id": current_agent.id,
        "agent_name": current_agent.name,
        "role": current_agent.role
    }
