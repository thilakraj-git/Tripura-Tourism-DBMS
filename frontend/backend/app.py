"""
Tripura Terra: Main Application Entry Point
FastAPI web application serving RESTful APIs, OpenAPI interactive documentation,
and high-fidelity static travel-tech frontend.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database.db_manager import init_db, execute_query_one
from database.seeds import seed_database
from backend.routers import destinations, culture_eco, itinerary, analytics, research, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify database initialization on startup
    db_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "tripura_terra.db")
    if not os.path.exists(db_file):
        print("[Startup] Database not detected. Initializing schema and seed dataset...")
        seed_database()
    else:
        # Check if table exists
        try:
            check = execute_query_one("SELECT COUNT(*) as count FROM districts")
            if not check or check["count"] == 0:
                print("[Startup] Database empty. Running seed populator...")
                seed_database()
        except Exception:
            print("[Startup] Re-initializing database...")
            seed_database()
    yield

app = FastAPI(
    title="Tripura Terra API",
    description="Intelligent Digital Platform for Sustainable Eco & Cultural Tourism in Tripura",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(users.router)
app.include_router(destinations.router)
app.include_router(culture_eco.router)
app.include_router(itinerary.router)
app.include_router(analytics.router)
app.include_router(research.router)

# Health Check
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Tripura Terra Core Engine",
        "database": "SQLite 3.x 3NF Normalized",
        "version": "1.0.0"
    }

# Mount Frontend Static Directory
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
frontend_dir = os.path.join(project_root, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    def serve_frontend_root():
        index_file = os.path.join(frontend_dir, "index.html")
        return FileResponse(index_file)
