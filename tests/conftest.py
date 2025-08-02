import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import get_db, Base
from src.config import get_settings, Settings

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_clockbucks.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_test_settings() -> Settings:
    """Get test configuration."""
    return Settings(
        DEBUG=True,
        DATABASE_URL=SQLALCHEMY_DATABASE_URL,
        ENVIRONMENT="testing",
        SECRET_KEY="test-secret-key",
        RATE_LIMIT_ENABLED=False,
    )


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def override_get_settings():
    """Override settings dependency for testing."""
    return get_test_settings()


# Override dependencies
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_settings] = override_get_settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_participant_data():
    """Sample participant data for testing."""
    return {
        "name": "John Doe",
        "email": "john.doe@test.com",
        "hourly_rate": 75.0,
        "role": "Senior Developer",
        "department": "Engineering",
    }


@pytest.fixture
def sample_meeting_data():
    """Sample meeting data for testing."""
    return {
        "title": "Sprint Planning",
        "description": "Planning for next sprint",
        "duration_minutes": 60,
        "meeting_type": "planning",
        "participants": [
            {
                "name": "John Doe",
                "email": "john.doe@test.com",
                "hourly_rate": 75.0,
                "role": "Senior Developer",
            },
            {
                "name": "Jane Smith",
                "email": "jane.smith@test.com",
                "hourly_rate": 85.0,
                "role": "Product Manager",
            },
        ],
    }
