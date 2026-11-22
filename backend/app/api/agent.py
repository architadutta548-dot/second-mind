
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.agent_engine import (
    create_research_plan,
    collect_information
)
from app.services.source_comparator import compare_sources

router = APIRouter(
    prefix="/agent",
    tags=["Autonomous Agent"]
)


# ==========================================
# REQUEST MODELS
# ==========================================

class ResearchRequest(BaseModel):
    goal: str


class SearchRequest(BaseModel):
    query: str
    max_results: int = Field(default=5, ge=1, le=20)


# ==========================================
# 1. RESEARCH PLANNING API
# ==========================================

@router.post("/plan")
def plan_research(request: ResearchRequest):

    return create_research_plan(request.goal)


# ==========================================
# 2. INFORMATION COLLECTION API
# ==========================================

@router.post("/search")
def search_information(request: SearchRequest):

    return collect_information(
        query=request.query,
        max_results=request.max_results
    )

# ==========================================
# 3. SOURCE COMPARISON API
# ==========================================

@router.post("/compare")
def compare_research_sources(request: SearchRequest):

    collected = collect_information(
        query=request.query,
        max_results=request.max_results
    )

    if collected["status"] != "success":
        return {
            "status": "collection_failed",
            "collection": collected
        }

    comparison = compare_sources(
        collected["results"]
    )

    return {
        "status": "success",
        "research_query": request.query,
        "comparison": comparison
    }
