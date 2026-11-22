
from app.database import SessionLocal
from app.models.agent import Agent


def create_agent():
    db = SessionLocal()

    try:
        existing_agent = db.query(Agent).filter(
            Agent.name == "Reasoning Agent"
        ).first()

        if existing_agent:
            print("Reasoning Agent already exists.")
            print("Agent ID:", existing_agent.id)
            return

        agent = Agent(
            name="Reasoning Agent",
            role="reasoner",
            description=(
                "Analyzes authorized knowledge, "
                "discovers relationships, and generates hypotheses."
            ),
            status="active"
        )

        db.add(agent)
        db.commit()
        db.refresh(agent)

        print("Reasoning Agent created successfully!")
        print("Agent ID:", agent.id)

    except Exception as error:
        db.rollback()
        print("ERROR:", error)

    finally:
        db.close()


if __name__ == "__main__":
    create_agent()
