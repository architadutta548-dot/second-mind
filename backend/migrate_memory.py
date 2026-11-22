
import sqlite3

connection = sqlite3.connect("second_mind.db")
cursor = connection.cursor()

columns = [
    ("owner_agent_id", "INTEGER REFERENCES agents(id)"),
    ("visibility", "VARCHAR(20) NOT NULL DEFAULT 'private'"),
    ("verification_status", "VARCHAR(50) NOT NULL DEFAULT 'unverified'"),
    ("source", "VARCHAR(500)"),
    ("updated_at", "DATETIME"),
]

existing_columns = {
    row[1]
    for row in cursor.execute("PRAGMA table_info(memories)").fetchall()
}

try:
    for column_name, column_type in columns:
        if column_name not in existing_columns:
            cursor.execute(
                f"ALTER TABLE memories ADD COLUMN {column_name} {column_type}"
            )
            print(f"Added column: {column_name}")
        else:
            print(f"Already exists: {column_name}")

    connection.commit()
    print("Memory migration completed successfully!")

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()
