"""
The Blind Spot — Quick Launch Server Script
Starts the FastAPI application and serves both API and Web UI.
"""
import sys
import uvicorn
from backend.config import settings

def main():
    print("=" * 65)
    print("   THE BLIND SPOT — AI Critical Thinking Companion")
    print("   Challenge: PromptWars 2026")
    print("=" * 65)
    print(f" * Server running on: http://{settings.HOST}:{settings.PORT}")
    print(" * Press Ctrl+C to terminate.")
    print("=" * 65)
    uvicorn.run(
        "backend.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False
    )

if __name__ == "__main__":
    main()
