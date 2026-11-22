
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.memory import Memory

from app.services.embedding_service import (
    generate_embedding,
    cosine_similarity
)

from app.services.knowledge_expansion import (
    expand_knowledge
)

router = APIRouter(
    prefix="/memories",
    tags=["Memory"]
)


# ---------------------------------
# Request models and validation
# ---------------------------------

class MemoryCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    category: str = Field(default="general", min_length=1, max_length=100)


class MemoryUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    category: str | None = Field(default=None, min_length=1, max_length=100)


# ---------------------------------
# Create a new memory
# ---------------------------------

@router.post("/")
def create_memory(
    memory_data: MemoryCreate,
    db: Session = Depends(get_db)
):

    title = memory_data.title.strip()
    content = memory_data.content.strip()
    category = memory_data.category.strip()

    if not title or not content or not category:
        raise HTTPException(
            status_code=400,
            detail="Title, content and category cannot be empty."
        )

    # Check exact duplicate
    existing_memories = db.query(Memory).all()

    for memory in existing_memories:

        if (
            memory.title.strip().lower() == title.lower()
            and memory.content.strip().lower() == content.lower()
        ):
            raise HTTPException(
                status_code=409,
                detail=f"Duplicate memory found. Existing memory ID: {memory.id}"
            )

    # Generate embedding
    text_to_embed = f"{title}. {content}"
    vector = generate_embedding(text_to_embed)

    # Create memory
    new_memory = Memory(
        title=title,
        content=content,
        category=category,
        embedding=vector
    )

    db.add(new_memory)
    db.commit()
    db.refresh(new_memory)

    # Find connections with existing memories
    expansion_result = expand_knowledge(
        new_memory,
        existing_memories
    )

    return {
        "message": "Memory saved successfully!",
        "memory": {
            "id": new_memory.id,
            "title": new_memory.title,
            "content": new_memory.content,
            "category": new_memory.category,
            "embedding_dimensions": len(vector)
        },
        "knowledge_expansion": expansion_result
    }


# ---------------------------------
# Get all memories
# ---------------------------------

@router.get("/")
def get_memories(db: Session = Depends(get_db)):

    memories = db.query(Memory).order_by(
        Memory.created_at.desc()
    ).all()

    return memories


# ---------------------------------
# Search memories
# ---------------------------------

@router.get("/search")
def search_memories(
    query: str = Query(min_length=1),
    db: Session = Depends(get_db),
    limit: int = Query(default=5, ge=1, le=20),
    min_similarity: float = Query(default=0.0, ge=0.0, le=1.0)
):

    query = query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty."
        )

    query_vector = generate_embedding(query)

    memories = db.query(Memory).filter(
        Memory.embedding.isnot(None)
    ).all()

    results = []

    for memory in memories:

        score = cosine_similarity(
            query_vector,
            memory.embedding
        )

        if score >= min_similarity:

            results.append({
                "id": memory.id,
                "title": memory.title,
                "content": memory.content,
                "category": memory.category,
                "similarity_score": round(score, 4)
            })

    results.sort(
        key=lambda item: item["similarity_score"],
        reverse=True
    )

    return {
        "query": query,
        "total_memories_searched": len(memories),
        "minimum_similarity": min_similarity,
        "results_returned": min(limit, len(results)),
        "results": results[:limit]
    }


# ---------------------------------
# Update an existing memory
# ---------------------------------

@router.put("/{memory_id}")
def update_memory(
    memory_id: int,
    memory_data: MemoryUpdate,
    db: Session = Depends(get_db)
):

    memory = db.query(Memory).filter(
        Memory.id == memory_id
    ).first()

    if memory is None:
        raise HTTPException(
            status_code=404,
            detail="Memory not found."
        )

    updates = memory_data.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update."
        )

    for field, value in updates.items():

        if isinstance(value, str):
            value = value.strip()

            if not value:
                raise HTTPException(
                    status_code=400,
                    detail=f"{field} cannot be empty."
                )

        setattr(memory, field, value)

    # Regenerate embedding if title or content changed
    if "title" in updates or "content" in updates:

        text_to_embed = f"{memory.title}. {memory.content}"

        memory.embedding = generate_embedding(text_to_embed)

    db.commit()
    db.refresh(memory)

    return {
        "message": "Memory updated successfully!",
        "memory": {
            "id": memory.id,
            "title": memory.title,
            "content": memory.content,
            "category": memory.category,
            "embedding_dimensions": (
                len(memory.embedding)
                if memory.embedding else 0
            )
        }
    }


# ---------------------------------
# Delete an existing memory
# ---------------------------------

@router.delete("/{memory_id}")
def delete_memory(
    memory_id: int,
    db: Session = Depends(get_db)
):

    memory = db.query(Memory).filter(
        Memory.id == memory_id
    ).first()

    if memory is None:
        raise HTTPException(
            status_code=404,
            detail="Memory not found."
        )

    deleted_memory = {
        "id": memory.id,
        "title": memory.title
    }

    db.delete(memory)
    db.commit()

    return {
        "message": "Memory deleted successfully!",
        "deleted_memory": deleted_memory
    }
