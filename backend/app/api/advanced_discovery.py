
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.memory import Memory

from app.services.advanced_discovery import (
    discover_advanced_connections
)

router = APIRouter(
    prefix="/advanced-discovery",
    tags=["Advanced Discovery"]
)


@router.get("/")
def get_advanced_discoveries(
    similarity_threshold: float = Query(
        default=0.65,
        ge=0.0,
        le=1.0
    ),
    db: Session = Depends(get_db)
):

    memories = db.query(Memory).all()

    result = discover_advanced_connections(
        memories,
        similarity_threshold
    )

    return result
