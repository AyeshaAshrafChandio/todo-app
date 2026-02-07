"""
FastAPI application entry point for Todo Backend.

This module initializes the FastAPI application, configures middleware,
sets up database connections, and registers API routes.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.connection import init_db, close_db, engine
from app.middleware.performance import PerformanceMonitoringMiddleware, setup_performance_monitoring


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.

    This function handles:
    - Database initialization on startup (creating tables)
    - Database connection cleanup on shutdown

    Args:
        app: FastAPI application instance

    Yields:
        None: Control to the application during its lifetime
    """
    # Startup: Initialize database tables
    print("Starting up: Initializing database...")
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

    # Setup performance monitoring
    print("Setting up performance monitoring...")
    try:
        setup_performance_monitoring(engine)
        print("Performance monitoring enabled")
    except Exception as e:
        print(f"Warning: Could not enable performance monitoring: {e}")

    # Yield control to the application
    yield

    # Shutdown: Close database connections
    print("Shutting down: Closing database connections...")
    try:
        close_db()
        print("Database connections closed successfully")
    except Exception as e:
        print(f"Error closing database connections: {e}")


# Initialize FastAPI application with lifespan manager
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-ready FastAPI backend for Todo application with PostgreSQL persistence",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Configure CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add performance monitoring middleware
app.add_middleware(PerformanceMonitoringMiddleware)


# Root endpoint for health check
@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint for API health check.

    Returns:
        dict: API status and version information
    """
    return {
        "status": "ok",
        "message": "Todo Backend API is running",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        dict: Health status of the application
    """
    return {
        "status": "healthy",
        "database": "connected"
    }


# Register API routes
from app.routes import tasks, auth, teams, team_members, task_shares, chat, dashboard, websocket

# Include authentication routes (routes have /api/auth prefix)
app.include_router(auth.router)

# Include task routes (routes already have /api/{user_id}/tasks prefix)
app.include_router(tasks.router)

# Include team routes (routes have /api/teams prefix)
app.include_router(teams.router)

# Include team member routes (routes have /api/teams prefix)
app.include_router(team_members.router)

# Include task sharing routes (routes have /api/tasks prefix)
app.include_router(task_shares.router)

# Include chat routes (routes have /api/chat prefix) - Spec 005
app.include_router(chat.router)

# Include dashboard routes (routes have /api/dashboard prefix) - Spec 008
app.include_router(dashboard.router)

# Include WebSocket routes (routes have /api/ws endpoint) - Phase 7
app.include_router(websocket.router)


if __name__ == "__main__":
    import uvicorn

    # Run the application with uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
