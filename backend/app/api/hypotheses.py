
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.memory import Memory

from app.services.pattern_discovery import discover_patterns
from app.services.hypothesis_engine import generate_hypotheses
from app.services.verification_service import verify_hypotheses
from app.services.self_evaluation import evaluate_hypotheses

router = APIRouter(
    prefix="/hypotheses",
    tags=["Hypothesis Generation"]
)


@router.get("/")
def get_hypotheses(db: Session = Depends(get_db)):
    memories = db.query(Memory).all()

    # Stage 1: Discover patterns
    pattern_data = discover_patterns(memories)

    # Stage 2: Generate hypotheses
    hypotheses = generate_hypotheses(pattern_data)

    # Stage 3: Verify supporting evidence
    verification = verify_hypotheses(
        hypotheses,
        pattern_data
    )

    # Stage 4: Evaluate evidence quality
    evaluation = evaluate_hypotheses(verification)

    return {
        "generation": hypotheses,
        "verification": verification,
        "evaluation": evaluation
    }
