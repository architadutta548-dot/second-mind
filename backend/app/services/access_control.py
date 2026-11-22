
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.memory import Memory
from app.models.memory_access import MemoryAccessGrant


def grant_memory_access(
    db: Session,
    memory_id: int,
    owner_agent_id: int,
    recipient_agent_id: int,
    permission: str = "read"
):
    # Validate permission
    if permission not in ["read"]:
        return {
            "status": "error",
            "message": "Invalid permission."
        }

    # Find memory
    memory = db.query(Memory).filter(
        Memory.id == memory_id
    ).first()

    if not memory:
        return {
            "status": "error",
            "message": "Memory not found."
        }

    # Verify ownership
    if memory.owner_agent_id != owner_agent_id:
        return {
            "status": "error",
            "message": "Agent does not own this memory."
        }

    # Verify both agents
    owner = db.query(Agent).filter(
        Agent.id == owner_agent_id
    ).first()

    recipient = db.query(Agent).filter(
        Agent.id == recipient_agent_id
    ).first()

    if not owner or not recipient:
        return {
            "status": "error",
            "message": "Agent not found."
        }

    if owner_agent_id == recipient_agent_id:
        return {
            "status": "error",
            "message": "Cannot share memory with the same agent."
        }

    # Check existing permission
    grant = db.query(MemoryAccessGrant).filter(
        MemoryAccessGrant.memory_id == memory_id,
        MemoryAccessGrant.recipient_agent_id == recipient_agent_id
    ).first()

    if grant:
        grant.permission = permission
        grant.status = "active"
    else:
        grant = MemoryAccessGrant(
            memory_id=memory_id,
            owner_agent_id=owner_agent_id,
            recipient_agent_id=recipient_agent_id,
            permission=permission,
            status="active"
        )

        db.add(grant)

    db.commit()

    return {
        "status": "success",
        "message": "Memory access granted.",
        "memory_id": memory_id,
        "owner_agent_id": owner_agent_id,
        "recipient_agent_id": recipient_agent_id,
        "permission": permission
    }


def revoke_memory_access(
    db: Session,
    memory_id: int,
    owner_agent_id: int,
    recipient_agent_id: int
):
    memory = db.query(Memory).filter(
        Memory.id == memory_id
    ).first()

    if not memory or memory.owner_agent_id != owner_agent_id:
        return {
            "status": "error",
            "message": "Memory ownership verification failed."
        }

    grant = db.query(MemoryAccessGrant).filter(
        MemoryAccessGrant.memory_id == memory_id,
        MemoryAccessGrant.owner_agent_id == owner_agent_id,
        MemoryAccessGrant.recipient_agent_id == recipient_agent_id,
        MemoryAccessGrant.status == "active"
    ).first()

    if not grant:
        return {
            "status": "error",
            "message": "Active permission not found."
        }

    grant.status = "revoked"
    db.commit()

    return {
        "status": "success",
        "message": "Memory access revoked.",
        "memory_id": memory_id,
        "recipient_agent_id": recipient_agent_id
    }


def can_access_memory(
    db: Session,
    memory_id: int,
    agent_id: int
):
    memory = db.query(Memory).filter(
        Memory.id == memory_id
    ).first()

    if not memory:
        return False

    # Owners can access their own memories
    if memory.owner_agent_id == agent_id:
        return True

    # Other agents need an active permission
    grant = db.query(MemoryAccessGrant).filter(
        MemoryAccessGrant.memory_id == memory_id,
        MemoryAccessGrant.recipient_agent_id == agent_id,
        MemoryAccessGrant.status == "active",
        MemoryAccessGrant.permission == "read"
    ).first()

    return grant is not None
