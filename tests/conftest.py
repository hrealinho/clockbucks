import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import get_db, Base

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


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
    return {
        "name": "John Doe",
        "email": "john.doe@test.com",
        "hourly_rate": 75.0,
        "role": "Senior Developer",
        "department": "Engineering",
    }


@pytest.fixture
def sample_meeting_data():
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
