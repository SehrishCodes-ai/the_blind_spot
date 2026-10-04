import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Settings:
    """Application configuration and settings."""
    APP_NAME: str = "The Blind Spot — AI Critical Thinking Companion"
    APP_VERSION: str = "1.0.0"
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Google Gemini API configuration
    # Primary model recommendation from Gemini API Skill: gemini-3.8-flash (or gemini-2.5-flash fallback)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    FALLBACK_MODEL: str = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash")
    
    # Request limits for safety and efficiency
    MAX_DECISION_LENGTH: int = 500
    MAX_REASONING_LENGTH: int = 4000
    MAX_CONTEXT_LENGTH: int = 2000

settings = Settings()
