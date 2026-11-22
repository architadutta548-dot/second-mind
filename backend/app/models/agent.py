
from sqlalchemy import Column, Integer, String, DateTime, func

from app.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False, unique=True)

    role = Column(String(100), nullable=False)

    description = Column(String(500), nullable=True)

    status = Column(String(20), default="active", nullable=False)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )
