
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.memory import Memory

from app.services.embedding_service import (
    generate_embedding,
    cosine_similarity
)

from app.services.reasoning_service import (
    reason_about_knowledge
)

router = APIRouter(
    prefix="/reasoning",
    tags=["AI Reasoning"]
)


@router.get("/")
def reason_about_query(
    query: str = Query(min_length=1),
    limit: int = Query(default=5, ge=1, le=20),
    min_similarity: float = Query(
        default=0.30,
        ge=0.0,
        le=1.0
    ),
    db: Session = Depends(get_db)
):

    query = query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    query_vector = generate_embedding(query)

    memories = db.query(Memory).filter(
        Memory.embedding.isnot(None)
    ).all()

    ranked_memories = []

    for memory in memories:

        score = cosine_similarity(
            query_vector,
            memory.embedding
        )

        if score >= min_similarity:
            ranked_memories.append({
                "memory": memory,
                "score": score
            })

    ranked_memories.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    selected_memories = ranked_memories[:limit]

    relevant_memories = [
        item["memory"]
        for item in selected_memories
    ]

    result = reason_about_knowledge(
        query,
        relevant_memories
    )

    result["retrieval"] = {
        "total_memories_searched": len(memories),
        "minimum_similarity": min_similarity,
        "memories_qualifying": len(ranked_memories),
        "memories_selected": len(selected_memories),
        "similarity_scores": [
            {
                "memory_id": item["memory"].id,
                "similarity": round(item["score"], 4)
            }
            for item in selected_memories
        ]
    }

    return result
