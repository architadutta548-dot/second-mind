
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models.agent_credential import AgentCredential
from app.services.agent_auth import generate_agent_api_key


def main():
    db = SessionLocal()

    try:
        agent_ids = [1, 2]

        old_keys = db.query(AgentCredential).filter(
            AgentCredential.agent_id.in_(agent_ids),
            AgentCredential.status == "active"
        ).all()

        for key in old_keys:
            key.status = "revoked"
            key.revoked_at = datetime.now(timezone.utc)

        db.commit()

        print("Previous active keys revoked.")

        for agent_id in agent_ids:
            result = generate_agent_api_key(db, agent_id)

            if result["status"] == "success":
                print(f"New API key generated for Agent {agent_id}.")
                print("Store the credential securely.")
            else:
                print(
                    f"Error for agent {agent_id}: "
                    f"{result['message']}"
                )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
