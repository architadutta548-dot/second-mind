
import hashlib
import secrets
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.agent_credential import AgentCredential


def hash_api_key(api_key: str) -> str:
    """Return the SHA-256 hash of an API key."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def generate_agent_api_key(
    db: Session,
    agent_id: int
) -> dict:
    """Generate and store a new API key for an agent."""

    agent = db.query(Agent).filter(
        Agent.id == agent_id
    ).first()

    if not agent:
        return {
            "status": "error",
            "message": "Agent not found."
        }

    if agent.status != "active":
        return {
            "status": "error",
            "message": "Agent is not active."
        }

    # Generate a high-entropy API key.
    api_key = "sm_" + secrets.token_urlsafe(48)

    credential = AgentCredential(
        agent_id=agent_id,
        key_hash=hash_api_key(api_key),
        key_prefix=api_key[:12],
        status="active"
    )

    try:
        db.add(credential)
        db.commit()
        db.refresh(credential)

        return {
            "status": "success",
            "message": "API key generated. Save it securely; it will not be shown again.",
            "agent_id": agent_id,
            "credential_id": credential.id,
            "api_key": api_key
        }

    except Exception:
        db.rollback()
        raise


def verify_agent_api_key(
    db: Session,
    api_key: str
):
    """Verify an API key and return its active agent."""

    if not api_key or not api_key.startswith("sm_"):
        return None

    key_hash = hash_api_key(api_key)

    credential = db.query(AgentCredential).filter(
        AgentCredential.key_hash == key_hash,
        AgentCredential.status == "active"
    ).first()

    if not credential:
        return None

    agent = db.query(Agent).filter(
        Agent.id == credential.agent_id,
        Agent.status == "active"
    ).first()

    return agent


def revoke_agent_api_key(
    db: Session,
    credential_id: int,
    agent_id: int
) -> dict:
    """Revoke an API key belonging to the specified agent."""

    credential = db.query(AgentCredential).filter(
        AgentCredential.id == credential_id,
        AgentCredential.agent_id == agent_id,
        AgentCredential.status == "active"
    ).first()

    if not credential:
        return {
            "status": "error",
            "message": "Active credential not found."
        }

    credential.status = "revoked"
    credential.revoked_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "status": "success",
        "message": "API key revoked.",
        "credential_id": credential_id,
        "agent_id": agent_id
    }
