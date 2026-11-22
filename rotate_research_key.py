
from app.database import SessionLocal
from app.models.agent_credential import AgentCredential
from app.services.agent_auth import generate_agent_api_key


def main():
    db = SessionLocal()

    try:
        result = generate_agent_api_key(db, 1)

        if result["status"] == "success":
            print("Research Agent key generated successfully!")
            print("Agent ID:", result["agent_id"])
            print("Credential ID:", result["credential_id"])
            print("API key generated. Store it securely; do not share it.")
            print("Keep this key private.")
        else:
            print("Error:", result["message"])

    except Exception as e:
        db.rollback()
        print("Error:", e)

    finally:
        db.close()


if __name__ == "__main__":
    main()
