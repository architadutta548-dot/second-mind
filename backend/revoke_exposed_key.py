
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models.agent import Agent
from app.models.agent_credential import AgentCredential


db = SessionLocal()

try:
    credential = db.query(AgentCredential).filter(
        AgentCredential.id == 9,
        AgentCredential.agent_id == 1,
        AgentCredential.status == "active"
    ).first()

    if credential:
        credential.status = "revoked"
        credential.revoked_at = datetime.now(timezone.utc)

        db.commit()

        print("Exposed Research Agent key revoked successfully!")
    else:
        print("Credential not found or already revoked.")

except Exception as e:
    db.rollback()
    print("Error:", e)

finally:
    db.close()
