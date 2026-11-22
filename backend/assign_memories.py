
from app.database import SessionLocal
from app.models.agent import Agent
from app.models.memory import Memory


def assign_memories():
    db = SessionLocal()

    try:
        # Find the Research Agent
        research_agent = db.query(Agent).filter(
            Agent.name == "Research Agent"
        ).first()

        if not research_agent:
            print("ERROR: Research Agent not found.")
            return

        # Find memories without an assigned owner
        memories = db.query(Memory).filter(
            Memory.owner_agent_id.is_(None)
        ).all()

        # Assign memories to Research Agent
        for memory in memories:
            memory.owner_agent_id = research_agent.id
            memory.visibility = "private"

        db.commit()

        print("Memory assignment completed successfully!")
        print("Agent:", research_agent.name)
        print("Agent ID:", research_agent.id)
        print("Memories assigned:", len(memories))

    except Exception as error:
        db.rollback()
        print("ERROR: Memory assignment failed.")
        print(error)

    finally:
        db.close()


if __name__ == "__main__":
    assign_memories()
