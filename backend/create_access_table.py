
from app.database import Base, engine

# Register all models with SQLAlchemy
from app.models.memory import Memory
from app.models.agent import Agent
from app.models.memory_access import MemoryAccessGrant


def create_access_table():
    try:
        Base.metadata.create_all(bind=engine)

        print("Database table creation completed!")

        print("Registered models:")
        print("- Memory")
        print("- Agent")
        print("- MemoryAccessGrant")

    except Exception as error:
        print("ERROR:", error)


if __name__ == "__main__":
    create_access_table()
