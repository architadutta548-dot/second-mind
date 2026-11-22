
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, func

from app.database import Base


class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)

    content = Column(Text, nullable=False)

    category = Column(
        String(100),
        default="general"
    )

    embedding = Column(JSON, nullable=True)

    # Agent ownership
    owner_agent_id = Column(
        Integer,
        ForeignKey("agents.id"),
        nullable=True
    )

    # Memory access control
    visibility = Column(
        String(20),
        default="private",
        nullable=False
    )

    # Evidence verification status
    verification_status = Column(
        String(50),
        default="unverified",
        nullable=False
    )

    # Original information source
    source = Column(String(500), nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
