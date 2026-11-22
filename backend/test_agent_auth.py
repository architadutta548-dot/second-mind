
from app.database import SessionLocal
from app.services.agent_auth import verify_agent_api_key

db = SessionLocal()

try:
    print("Agent authentication service loaded successfully.")
    print("Credential records:", db.query(
        __import__(
            "app.models.agent_credential",
            fromlist=["AgentCredential"]
        ).AgentCredential
    ).count())

finally:
    db.close()
