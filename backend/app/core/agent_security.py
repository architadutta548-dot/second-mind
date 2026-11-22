
from fastapi import (
    Depends,
    Header,
    HTTPException,
    status,
    Security
)
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.agent import Agent
from app.services.agent_auth import verify_agent_api_key


agent_api_key_header = APIKeyHeader(
    name="X-Agent-Key",
    scheme_name="AgentAPIKey",
    description="Enter your private Second Mind Agent API key.",
    auto_error=False
)


def get_current_agent(
    db: Session = Depends(get_db),
    x_agent_key: str = Security(agent_api_key_header)
) -> Agent:

    if not x_agent_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Agent API key is required."
        )

    agent = verify_agent_api_key(
        db=db,
        api_key=x_agent_key
    )

    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive agent API key."
        )

    return agent
