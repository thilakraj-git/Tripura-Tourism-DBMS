"""
Tripura Terra: Server Launcher
Initializes the database and starts the FastAPI application with Uvicorn.
Accessible at: http://127.0.0.1:8000
Interactive API Docs at: http://127.0.0.1:8000/api/docs
"""

import os
import sys
import threading
import time
import webbrowser
import uvicorn

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.seeds import seed_database
from database.db_manager import DB_PATH

def auto_launch_browser():
    """Automatically launches the user's default browser after server initializes."""
    time.sleep(1.5)
    try:
        webbrowser.open("http://127.0.0.1:8000")
    except Exception as e:
        print(f"[Launcher] Could not open browser automatically: {e}")

def main():
    print("============================================================================")
    print("               TRIPURA TOURISM — OFFICIAL SMART WEB APPLICATION             ")
    print("============================================================================")
    print("Architecture: 3NF Relational Schema (Foreign Keys, Triggers, Views)")
    print("Engines: Eco Responsibility Index (ERI) & Multi-Criteria Recommender")
    print("----------------------------------------------------------------------------")

    if not os.path.exists(DB_PATH):
        print("[Database] SQLite database not detected. Initializing schema & seeds...")
        seed_database()
    else:
        print(f"[Database] Active database found at: {DB_PATH}")

    # Support dynamic cloud hosting port (Render, Railway, Heroku, Fly.io, etc.)
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    is_cloud = bool(os.environ.get("RENDER") or os.environ.get("PORT") or os.environ.get("RAILWAY_ENVIRONMENT"))

    print(f"\nStarting Web Application Server on {host}:{port}...")
    print(f"  • Web Application:   http://localhost:{port}")
    print(f"  • API Documentation: http://localhost:{port}/api/docs")
    print(f"  • Demo Accounts:     admin@tripuraterra.in | marcus.eco@traveler.org")
    print("----------------------------------------------------------------------------")

    # Only auto-open browser in local environment
    if not is_cloud:
        print("Opening application in your web browser automatically...\n")
        threading.Thread(target=auto_launch_browser, daemon=True).start()

    # Run Uvicorn server
    uvicorn.run("backend.app:app", host=host, port=port, reload=False, log_level="info")

if __name__ == "__main__":
    main()

