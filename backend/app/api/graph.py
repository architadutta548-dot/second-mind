
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.memory import Memory
from app.services.knowledge_graph import build_graph_from_memories

router = APIRouter(
    prefix="/graph",
    tags=["Knowledge Graph"]
)


@router.get("/")
def get_knowledge_graph(db: Session = Depends(get_db)):

    memories = db.query(Memory).all()

    graph_data = build_graph_from_memories(memories)

    return graph_data


@router.get("/connections/{concept}")
def get_concept_connections(
    concept: str,
    db: Session = Depends(get_db)
):

    memories = db.query(Memory).all()

    graph_data = build_graph_from_memories(memories)

    # Find the requested concept
    matching_node = next(
        (
            node for node in graph_data["nodes"]
            if node["id"].lower() == concept.lower()
        ),
        None
    )

    if matching_node is None:
        raise HTTPException(
            status_code=404,
            detail=f"Concept '{concept}' was not found."
        )

    # Find relationships involving this concept
    connections = []

    for edge in graph_data["edges"]:

        if (
            edge["source"].lower() == concept.lower()
            or edge["target"].lower() == concept.lower()
        ):

            related_concept = (
                edge["target"]
                if edge["source"].lower() == concept.lower()
                else edge["source"]
            )

            connections.append({
                "related_concept": related_concept,
                "relationship": edge["relationship"],
                "evidence_type": edge["evidence_type"],
                "evidence_count": edge["evidence_count"],
                "supporting_memory_ids": edge["supporting_memory_ids"],
                "strength": edge["strength"],
                "confidence": edge["confidence"]
            })

    return {
        "concept": matching_node["id"],
        "categories": matching_node["categories"],
        "memory_count": matching_node["memory_count"],
        "supporting_memory_ids": matching_node["supporting_memory_ids"],
        "total_connections": len(connections),
        "connections": connections
    }
