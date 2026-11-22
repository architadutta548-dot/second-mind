
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.agent import Agent
from app.models.agent_message import AgentMessage
from app.core.agent_security import get_current_agent
from app.services.agent_collaboration import process_research_message


router = APIRouter(
    prefix="/agent-communication",
    tags=["Agent Communication"]
)


class MessageCreate(BaseModel):
    receiver_agent_id: int = Field(gt=0)
    message_type: str = Field(default="general", max_length=50)
    content: str = Field(min_length=1, max_length=10000)


# Send a message
@router.post("/send")
def send_message(
    request: MessageCreate,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    receiver = db.query(Agent).filter(
        Agent.id == request.receiver_agent_id,
        Agent.status == "active"
    ).first()

    if receiver is None:
        raise HTTPException(
            status_code=404,
            detail="Active receiver agent not found."
        )

    if receiver.id == current_agent.id:
        raise HTTPException(
            status_code=400,
            detail="An agent cannot send a message to itself."
        )

    message = AgentMessage(
        sender_agent_id=current_agent.id,
        receiver_agent_id=receiver.id,
        message_type=request.message_type,
        content=request.content,
        status="sent"
    )

    try:
        db.add(message)
        db.commit()
        db.refresh(message)

        return {
            "status": "success",
            "message": "Agent message sent successfully.",
            "message_id": message.id,
            "sender_agent_id": message.sender_agent_id,
            "receiver_agent_id": message.receiver_agent_id,
            "message_type": message.message_type,
            "content": message.content,
            "created_at": (
                message.created_at.isoformat()
                if message.created_at else None
            )
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save agent message."
        )


# View inbox
@router.get("/inbox")
def get_inbox(
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    messages = (
        db.query(AgentMessage)
        .filter(
            AgentMessage.receiver_agent_id == current_agent.id
        )
        .order_by(AgentMessage.created_at.desc())
        .all()
    )

    return {
        "status": "success",
        "agent_id": current_agent.id,
        "total_messages": len(messages),
        "messages": [
            {
                "message_id": message.id,
                "sender_agent_id": message.sender_agent_id,
                "receiver_agent_id": message.receiver_agent_id,
                "message_type": message.message_type,
                "content": message.content,
                "status": message.status,
                "created_at": (
                    message.created_at.isoformat()
                    if message.created_at else None
                )
            }
            for message in messages
        ]
    }


# Process research message
@router.post("/process/{message_id}")
def process_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    if current_agent.role != "reasoner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the Reasoning Agent can process research messages."
        )

    result = process_research_message(
        db=db,
        message_id=message_id,
        reasoning_agent_id=current_agent.id
    )

    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

    return result
