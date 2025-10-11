# Testing Guide

This document explains how to run tests for the legal-mcp project.

## Test Structure

The project has two types of tests:

### Unit Tests
- **Location**: `store/tests/test_*.py` (marked with `@pytest.mark.unit`)
- **Requirements**: None (use mocked dependencies)
- **Speed**: Fast (~0.5s for 35 tests)
- **Purpose**: Test business logic in isolation

### Integration Tests
- **Location**: `store/tests/test_*_integration.py` (marked with `@pytest.mark.integration`)
- **Requirements**: Running PostgreSQL database with pgvector extension
- **Speed**: Slower (~several seconds)
- **Purpose**: Test full stack with real database

## Running Tests

### Prerequisites

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. For integration tests, ensure PostgreSQL is running:
```bash
docker-compose up -d postgres
```

### Run All Tests

```bash
pytest
```

### Run Only Unit Tests (Fast)

```bash
pytest -m unit
```

This runs all tests with mocked dependencies. No database required.

### Run Only Integration Tests

```bash
pytest -m integration
```

This requires a running PostgreSQL database. Configure via environment variables:

```bash
export TEST_POSTGRES_HOST=localhost
export TEST_POSTGRES_PORT=5432
export TEST_POSTGRES_USER=legal_mcp
export TEST_POSTGRES_PASSWORD=legal_mcp_password
export TEST_POSTGRES_DB=legal_mcp_test
```

### Run Specific Test File

```bash
pytest store/tests/test_repository.py -v
```

### Run Specific Test

```bash
pytest store/tests/test_repository.py::TestLegalTextRepository::test_add_legal_text -v
```

## Test Configuration

Test configuration is in `pytest.ini`:

- **Test discovery**: Looks for `test_*.py` files in `store/tests/`
- **Markers**: `unit` and `integration` for categorizing tests
- **Asyncio mode**: Auto-detects async tests

## Database Setup for Integration Tests

Integration tests use a separate test database (`legal_mcp_test` by default) to avoid affecting production data.

### Using Docker

```bash
# Start PostgreSQL with pgvector
docker-compose up -d postgres

# Tests will automatically create/drop tables
pytest -m integration
```

### Using Local PostgreSQL

1. Create test database:
```sql
CREATE DATABASE legal_mcp_test;
\c legal_mcp_test
CREATE EXTENSION vector;
```

2. Set environment variables:
```bash
export TEST_POSTGRES_HOST=localhost
export TEST_POSTGRES_PORT=5432
export TEST_POSTGRES_USER=your_user
export TEST_POSTGRES_PASSWORD=your_password
export TEST_POSTGRES_DB=legal_mcp_test
```

3. Run tests:
```bash
pytest -m integration
```

## Test Isolation

- **Unit tests**: Each test uses fresh mocks (no cleanup needed)
- **Integration tests**: Each test runs in a transaction that's rolled back after completion
- **Database schema**: Created once per session, dropped at end

## CI/CD Recommendations

For continuous integration:

1. **Always run unit tests** (fast, no dependencies):
```bash
pytest -m unit
```

2. **Run integration tests** in environments with database access:
```bash
pytest -m integration
```

3. **Run all tests** before merging:
```bash
pytest
```

## Writing New Tests

### Unit Test Example

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.unit
def test_my_function(mock_repository):
    """Test description"""
    mock_repository.method.return_value = expected_value
    result = my_function(mock_repository)
    assert result == expected_value
```

### Integration Test Example

```python
import pytest

@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_operation(test_repository):
    """Test description"""
    await test_repository.add_legal_text(legal_text)
    results = await test_repository.get_legal_text(filter)
    assert len(results) == 1
```

## Troubleshooting

### Integration tests fail with connection error

**Problem**: `socket.gaierror: [Errno 8] nodename nor servname provided`

**Solution**: Ensure PostgreSQL is running and environment variables are set correctly.

### Tests are slow

**Solution**: Run only unit tests with `pytest -m unit` for fast feedback during development.

### pgvector extension not found

**Problem**: `ERROR: extension "vector" does not exist`

**Solution**: Install pgvector extension:
```bash
# Using Docker (recommended)
docker-compose up -d postgres

# Or install locally
# See: https://github.com/pgvector/pgvector
```

## Coverage

To generate test coverage report:

```bash
pytest --cov=app --cov-report=html
```

Open `htmlcov/index.html` to view coverage details.
