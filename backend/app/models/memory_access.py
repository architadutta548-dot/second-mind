
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func
)

from app.database import Base


class MemoryAccessGrant(Base):
    __tablename__ = "memory_access_grants"

    id = Column(Integer, primary_key=True, index=True)

    memory_id = Column(
        Integer,
        ForeignKey("memories.id"),
        nullable=False
    )

    owner_agent_id = Column(
        Integer,
        ForeignKey("agents.id"),
        nullable=False
    )

    recipient_agent_id = Column(
        Integer,
        ForeignKey("agents.id"),
        nullable=False
    )

    permission = Column(
        String(20),
        default="read",
        nullable=False
    )

    status = Column(
        String(20),
        default="active",
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "memory_id",
            "recipient_agent_id",
            name="unique_memory_agent_grant"
        ),
    )
