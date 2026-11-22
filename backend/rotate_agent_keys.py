
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models.agent_credential import AgentCredential
from app.services.agent_auth import generate_agent_api_key


def main():
    db = SessionLocal()

    try:
        old_credentials = db.query(AgentCredential).filter(
            AgentCredential.agent_id.in_([1, 2]),
            AgentCredential.status == "active"
        ).all()

        for credential in old_credentials:
            credential.status = "revoked"
            credential.revoked_at = datetime.now(timezone.utc)

        db.commit()
        print("Previous active credentials revoked.")

        for agent_id in [1, 2]:
            result = generate_agent_api_key(db, agent_id)

            if result["status"] == "success":
                print(f"New API key generated for Agent {agent_id}.")
                print("Retrieve and store credentials securely.")
            else:
                print(f"Agent {agent_id}: {result['message']}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
