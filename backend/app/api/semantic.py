from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.memory import Memory

from app.services.semantic_discovery import (
    discover_semantic_connections
)

router = APIRouter(
    prefix="/semantic",
    tags=["Semantic Discovery"]
)


@router.get("/")
def get_semantic_connections(
    db: Session = Depends(get_db)
):
    memories = db.query(Memory).all()

    return discover_semantic_connections(memories)