
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    func
)

from app.database import Base


class AgentMessage(Base):
    __tablename__ = "agent_messages"

    id = Column(Integer, primary_key=True, index=True)

    sender_agent_id = Column(
        Integer,
        ForeignKey("agents.id"),
        nullable=False,
        index=True
    )

    receiver_agent_id = Column(
        Integer,
        ForeignKey("agents.id"),
        nullable=False,
        index=True
    )

    message_type = Column(
        String(50),
        nullable=False,
        default="general"
    )

    content = Column(Text, nullable=False)

    status = Column(
        String(20),
        nullable=False,
        default="sent"
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    read_at = Column(DateTime, nullable=True)
