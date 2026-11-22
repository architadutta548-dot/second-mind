from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.memory import Memory
from app.services.pattern_discovery import discover_patterns

router = APIRouter(
    prefix="/patterns",
    tags=["Pattern Discovery"]
)


@router.get("/")
def get_patterns(db: Session = Depends(get_db)):
    memories = db.query(Memory).all()

    return discover_patterns(memories)