from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from src.config import settings
from src.logging_config import app_logger
from src.database import init_db
from src.exceptions import ClockBucksException, map_exception_to_http
from src.middleware.security import (
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
)
from src.routes import meetings, participants

logger = logging.getLogger("clockbucks.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Application shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    description="""
    # Clock Bucks API - Meeting Cost Calculator

    A comprehensive backend service that calculates the cost of meetings based on participant salaries and hourly rates.

    ## Features
    - **Meeting Management**: Create, update, and track meetings with cost calculations
    - **Participant Management**: Manage participants with roles and hourly rates
    - **Cost Calculations**: Real-time cost tracking during meetings
    - **Statistics**: Meeting analytics and cost reporting
    - **Data Persistence**: File-based storage with plans for database integration

    ## Use Cases
    - Track meeting costs for budget planning
    - Optimize meeting efficiency by understanding cost implications
    - Generate cost reports for management and accounting
    - Real-time cost awareness during ongoing meetings

    ## Architecture
    - **FastAPI**: High-performance async Python web framework
    - **Pydantic**: Data validation and serialization
    - **Repository Pattern**: Clean separation of data access logic
    - **File Storage**: JSON-based persistence (interim solution)
    - **Comprehensive Testing**: pytest-based test suite
    
    ## Contact
    - **Developer**: Henrique Realinho
    - **Repository**: https://github.com/hrealinho/clockbucks
    """,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    contact={
        "name": "Clock Bucks API Support",
        "url": "https://github.com/hrealinho/clockbucks",
        "email": "support@clockbucks.com",
    },
    license_info={"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
    servers=[
        {"url": "http://localhost:8000", "description": "Development server"},
        {"url": "https://api.clockbucks.com", "description": "Production server"},
    ],
    tags_metadata=[
        {
            "name": "meetings",
            "description": "Operations with meetings. Create, read, update, delete meetings and calculate costs.",
            "externalDocs": {
                "description": "Meeting Management Documentation",
                "url": "https://docs.clockbucks.com/meetings",
            },
        },
        {
            "name": "participants",
            "description": "Manage meeting participants, their roles, and hourly rates.",
            "externalDocs": {
                "description": "Participant Management Documentation",
                "url": "https://docs.clockbucks.com/participants",
            },
        },
        {
            "name": "system",
            "description": "System health, metrics, and API information endpoints.",
        },
    ],
)

# Add middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(
        RateLimitMiddleware, calls=settings.RATE_LIMIT_PER_MINUTE, period=60
    )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(ClockBucksException)
async def custom_exception_handler(request: Request, exc: ClockBucksException):
    """Handle custom application exceptions."""
    http_exc = map_exception_to_http(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail,
        headers={"X-Request-ID": getattr(request.state, "request_id", "unknown")},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={"request_id": request_id},
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "details": {} if not settings.DEBUG else {"error": str(exc)},
        },
        headers={"X-Request-ID": request_id},
    )


# Include routers
app.include_router(meetings.router, prefix=settings.API_V1_STR, tags=["meetings"])
app.include_router(
    participants.router, prefix=settings.API_V1_STR, tags=["participants"]
)


# Root endpoints
@app.get(
    "/",
    tags=["system"],
    summary="API Information",
    description="Get basic API information and service details",
)
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs" if settings.DEBUG else None,
        "health_check": "/health",
    }


@app.get(
    "/health",
    tags=["system"],
    summary="Health Check",
    description="Check API health status for monitoring and load balancers",
)
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "clock-bucks-api",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get(
    "/metrics",
    tags=["system"],
    summary="Service Metrics",
    description="Get basic service metrics (extensible with Prometheus)",
)
async def metrics():
    """Basic metrics endpoint (can be extended with Prometheus)."""
    if not settings.ENABLE_METRICS:
        raise HTTPException(status_code=404, detail="Metrics not enabled")

    # Basic metrics - extend with prometheus_client for production
    return {
        "service": "clock-bucks-api",
        "version": settings.APP_VERSION,
        "uptime": "calculated_uptime_here",  # Implement actual uptime calculation
        "request_count": "total_requests_here",  # Implement request counter
    }
