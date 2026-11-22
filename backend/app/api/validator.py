
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.memory import Memory

from app.services.knowledge_graph import (
    build_graph_from_memories
)

from app.services.connection_validator import (
    validate_connections
)

router = APIRouter(
    prefix="/validator",
    tags=["Connection Validator"]
)


@router.get("/")
def get_validated_connections(
    db: Session = Depends(get_db)
):
    # Get all saved memories
    memories = db.query(Memory).all()

    # Build the knowledge graph
    graph_data = build_graph_from_memories(memories)

    # Extract graph relationships
    connections = graph_data["edges"]

    # Validate the relationships
    validation_result = validate_connections(
        connections
    )

    return validation_result
