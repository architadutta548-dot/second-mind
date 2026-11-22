
import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.agent_message import AgentMessage


def analyze_research_message(content: str) -> dict:
    """
    Basic rule-based research analysis.
    This is a prototype, not an LLM-powered engine.
    """

    content = content.strip()

    if not content:
        return {
            "status": "error",
            "message": "Research content is empty."
        }

    words = content.split()

    return {
        "status": "success",
        "analysis": {
            "summary": content[:500],
            "word_count": len(words),
            "key_observations": [
                "Research content received successfully.",
                "Content is ready for deeper reasoning."
            ],
            "conclusion": (
                "Further analysis is required before "
                "drawing a final conclusion."
            )
        }
    }


def process_research_message(
    db: Session,
    message_id: int,
    reasoning_agent_id: int
) -> dict:

    reasoning_agent = db.query(Agent).filter(
        Agent.id == reasoning_agent_id,
        Agent.status == "active",
        Agent.role == "reasoner"
    ).first()

    if reasoning_agent is None:
        return {
            "status": "error",
            "message": "Active reasoning agent not found."
        }

    research_message = db.query(AgentMessage).filter(
        AgentMessage.id == message_id,
        AgentMessage.receiver_agent_id == reasoning_agent_id
    ).first()

    if research_message is None:
        return {
            "status": "error",
            "message": "Research message not found."
        }

    if research_message.sender_agent_id == reasoning_agent_id:
        return {
            "status": "error",
            "message": "Cannot analyze your own outgoing message."
        }

    if research_message.status == "read":
        return {
            "status": "error",
            "message": "This research message has already been processed."
        }

    analysis_result = analyze_research_message(
        research_message.content
    )

    if analysis_result["status"] != "success":
        return analysis_result

    analysis_json = json.dumps(
        analysis_result["analysis"],
        ensure_ascii=False
    )

    try:
        research_message.status = "read"
        research_message.read_at = datetime.now()

        response_message = AgentMessage(
            sender_agent_id=reasoning_agent_id,
            receiver_agent_id=research_message.sender_agent_id,
            message_type="reasoning_analysis",
            content=analysis_json,
            status="sent"
        )

        db.add(response_message)
        db.commit()
        db.refresh(response_message)

        return {
            "status": "success",
            "message": "Research analyzed and response sent.",
            "reasoning_agent_id": reasoning_agent_id,
            "source_message_id": research_message.id,
            "response_message_id": response_message.id,
            "analysis": analysis_result["analysis"]
        }

    except Exception:
        db.rollback()
        raise
