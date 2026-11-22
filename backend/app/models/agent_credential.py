
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    func
)

from app.database import Base


class AgentCredential(Base):
    __tablename__ = "agent_credentials"

    id = Column(Integer, primary_key=True, index=True)

    agent_id = Column(
        Integer,
        ForeignKey("agents.id"),
        nullable=False,
        index=True
    )

    key_hash = Column(
        String(64),
        nullable=False,
        unique=True,
        index=True
    )

    key_prefix = Column(
        String(12),
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

    revoked_at = Column(
        DateTime,
        nullable=True
    )
