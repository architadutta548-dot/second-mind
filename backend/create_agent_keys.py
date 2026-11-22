
from app.database import SessionLocal
from app.services.agent_auth import generate_agent_api_key


def main():
    db = SessionLocal()

    try:
        for agent_id in [1, 2]:
            result = generate_agent_api_key(db, agent_id)

            if result["status"] == "success":
                print(
                    f"API key generated successfully "
                    f"for Agent {result['agent_id']}."
                )
                print("Store the credential securely.")
            else:
                print(f"Agent {agent_id}: {result['message']}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
