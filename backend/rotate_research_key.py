
from app.database import SessionLocal
from app.services.agent_auth import generate_agent_api_key


def main():
    db = SessionLocal()

    try:
        result = generate_agent_api_key(db, 1)

        if result["status"] == "success":
            print("Research Agent key generated successfully!")
            print("Agent ID:", result["agent_id"])
            print("Credential ID:", result["credential_id"])
            print("Store the API key securely.")
        else:
            print("Error:", result["message"])

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
