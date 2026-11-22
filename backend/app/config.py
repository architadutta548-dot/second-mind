
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_NAME = "Second Mind"
VERSION = "0.1.0"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./second_mind.db"
)

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "change-this-secret-key"
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
