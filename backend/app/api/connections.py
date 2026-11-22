
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.memory import Memory

from app.services.connection_discovery import (
    discover_cross_memory_connections
)

router = APIRouter(
    prefix="/connections",
    tags=["Cross-Memory Discovery"]
)


@router.get("/")
def get_cross_memory_connections(
    db: Session = Depends(get_db)
):
    memories = db.query(Memory).all()

    return discover_cross_memory_connections(memories)
