
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.memory import Memory

from app.services.cross_domain_discovery import (
    discover_cross_domain_connections
)

router = APIRouter(
    prefix="/discovery",
    tags=["Cross-Domain Discovery"]
)


@router.get("/")
def get_cross_domain_discoveries(
    db: Session = Depends(get_db)
):
    memories = db.query(Memory).all()

    return discover_cross_domain_connections(memories)
