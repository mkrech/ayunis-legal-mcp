# Local Development Setup

> **Note:** This project is configured for **local development** without Docker.
> PostgreSQL and Ollama are running directly on the host machine.

## Prerequisites

✅ PostgreSQL installed and running locally
✅ Ollama installed and running locally
✅ Python 3.10+ with uv package manager

## Required Ollama Model

Pull the required embedding model:

```bash
ollama pull ryanshillington/Qwen3-Embedding-4B:latest
```

## Environment Setup

### 1. Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` for **local development**:

```dotenv
# PostgreSQL - Local Installation
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_PASSWORD=postgres_password
POSTGRES_DB=legal_mcp

# Ollama - Local Installation  
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_AUTH_TOKEN=
OLLAMA_TIMEOUT=120
OLLAMA_BATCH_SIZE=50

# Store API - Local Development
LEGAL_API_BASE_URL=http://localhost:8000
```

### 3. Install Dependencies

```bash
# Install all dependencies with uv
uv sync

# This creates a virtual environment at .venv
```

## Database Setup

### 1. Create Database

```bash
# Connect to PostgreSQL
psql -d postgres

# Create database
CREATE DATABASE legal_mcp;

# Install pgvector extension
\c legal_mcp
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### 2. Run Migrations

```bash
# From project root
cd store
uv run alembic upgrade head
cd ..
```

## Running the Application

### Start Ollama

```bash
# If not already running
ollama serve
```

### Start Store API

```bash
# From project root (recommended)
uv run python run_api.py

# API will be available at:
# - http://localhost:8000
# - Docs: http://localhost:8000/docs
```

### Use CLI Tool

```bash
# List available legal codes
uv run legal-mcp list catalog

# Import a legal code
uv run legal-mcp import --code bgb

# Query a specific section
uv run legal-mcp query --code bgb --section "§ 433"

# Search semantically
uv run legal-mcp search --code bgb --query "Kaufvertrag"
```

## Development Workflow

### 1. Code Changes

- Edit files in `store/app/`, `cli/`, or `mcp/`
- The API auto-reloads with `--reload` flag
- CLI changes require re-running the command

### 2. Database Changes

```bash
# Create new migration
cd store
uv run alembic revision --autogenerate -m "Description"

# Apply migration
uv run alembic upgrade head
```

### 3. Run Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/cli/test_import_cmd.py

# Run with coverage
uv run pytest --cov=cli --cov=store
```

## Project Structure for Local Development

```
ayunis-legal-mcp/
├── .env                    # Local environment configuration
├── .venv/                  # Virtual environment (created by uv)
├── pyproject.toml          # Project dependencies (uv configuration)
├── cli/                    # CLI tool source code
│   ├── main.py
│   ├── commands/
│   └── ...
├── store/                  # Store API source code
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routers/
│   │   └── scrapers/
│   ├── alembic/            # Database migrations
│   └── ...
├── mcp/                    # MCP server source code
│   └── server/
└── tests/                  # Test suite
```

## Common Commands

```bash
# Sync dependencies
uv sync

# Add a new dependency
uv add <package-name>

# Run Store API
uv run uvicorn store.app.main:app --reload --port 8000

# Run CLI
uv run legal-mcp <command>

# Run tests
uv run pytest

# Database migrations
cd store && uv run alembic upgrade head
```

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
pg_isready

# List databases
psql -d postgres -c "\l"

# Check connection
psql -d legal_mcp -c "SELECT 1;"
```

### Ollama Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Verify model is installed
ollama list | grep Qwen3-Embedding
```

### Import Errors

```bash
# Verify Python environment
uv run python --version

# Check installed packages
uv pip list

# Re-sync dependencies
uv sync --reinstall
```

## Switching Between Local and Docker

To switch back to Docker setup:

1. Stop local services (API, Ollama, PostgreSQL)
2. Update `.env`:
   ```dotenv
   POSTGRES_HOST=postgres
   OLLAMA_BASE_URL=http://host.docker.internal:11434
   LEGAL_API_BASE_URL=http://store-api:8000
   ```
3. Start Docker services: `docker-compose up -d`

See [DOCKER_SETUP.md](DOCKER_SETUP.md) for Docker-specific instructions.
