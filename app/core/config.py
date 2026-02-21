import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration class to load API keys from environment variables
class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

settings = Settings()
