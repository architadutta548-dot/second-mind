
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.memory import Memory

from app.services.advanced_reasoning import (
    perform_advanced_reasoning
)

router = APIRouter(
    prefix="/advanced-reasoning",
    tags=["Advanced Cognitive Reasoning"]
)


@router.get("/")
def advanced_reasoning(
    query: str = Query(min_length=1),
    db: Session = Depends(get_db)
):
    query = query.strip()

    if not query:
        return {
            "status": "invalid_query",
            "message": "Query cannot be empty."
        }

    # Retrieve ALL saved memories,
    # including memories without stored embeddings.
    memories = db.query(Memory).all()

    # Convert SQLAlchemy objects into dictionaries.
    memory_data = [
        {
            "id": memory.id,
            "title": memory.title,
            "content": memory.content,
            "category": memory.category or "general"
        }
        for memory in memories
    ]

    # Perform advanced multi-memory reasoning.
    result = perform_advanced_reasoning(
        query,
        memory_data
    )

    # Add retrieval information.
    result["retrieval"] = {
        "total_memories_retrieved": len(memory_data)
    }

    return result
