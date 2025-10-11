"""
ABOUTME: Pytest configuration and shared fixtures for all tests
ABOUTME: Includes fixtures for database setup, test client, and integration test support
"""
import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.models import Base
from app.database import get_async_session
from app.dependencies import get_legal_text_repository
from app.repository import LegalTextRepository


# Test database configuration
TEST_POSTGRES_HOST = os.getenv("TEST_POSTGRES_HOST", "localhost")
TEST_POSTGRES_PORT = int(os.getenv("TEST_POSTGRES_PORT", "5432"))
TEST_POSTGRES_USER = os.getenv("TEST_POSTGRES_USER", "legal_mcp")
TEST_POSTGRES_PASSWORD = os.getenv("TEST_POSTGRES_PASSWORD", "legal_mcp_password")
TEST_POSTGRES_DB = os.getenv("TEST_POSTGRES_DB", "legal_mcp_test")

# Build test database URLs
TEST_ASYNC_DATABASE_URL = (
    f"postgresql+asyncpg://{TEST_POSTGRES_USER}:{TEST_POSTGRES_PASSWORD}"
    f"@{TEST_POSTGRES_HOST}:{TEST_POSTGRES_PORT}/{TEST_POSTGRES_DB}"
)


@pytest_asyncio.fixture(scope="session")
async def test_async_engine():
    """
    Create test database engine for the entire test session

    This fixture is session-scoped to reuse the same engine across all tests
    """
    engine = create_async_engine(
        TEST_ASYNC_DATABASE_URL,
        echo=False,
        future=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after tests complete
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_db_session(test_async_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session for each test

    This fixture creates a new session for each test and rolls back
    all changes after the test completes, ensuring test isolation
    """
    # Create a new session factory
    async_session_factory = async_sessionmaker(
        test_async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_factory() as session:
        # Begin a transaction
        await session.begin()

        yield session

        # Rollback the transaction to undo all changes
        await session.rollback()


@pytest.fixture
def test_repository(test_db_session) -> LegalTextRepository:
    """
    Create a test repository with the test database session
    """
    return LegalTextRepository(test_db_session)


@pytest.fixture
def integration_client(test_db_session) -> TestClient:
    """
    Create a test client with database dependency override for integration tests

    This client uses the test database session instead of the production database
    """
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_async_session] = override_get_db
    client = TestClient(app)

    yield client

    # Clean up dependency overrides
    app.dependency_overrides.clear()
