import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration class to load API keys from environment variables
class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

settings = Settings()
