# Command Reference - Local Development

## Datenbank Setup

### Datenbank erstellen
```bash
# PostgreSQL Datenbank erstellen
psql -d postgres -c "CREATE DATABASE legal_mcp;"

# pgvector Extension installieren
psql -d legal_mcp -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Datenbank prüfen
```bash
# Alle Datenbanken auflisten
psql -d postgres -c "SELECT datname FROM pg_database;"

# Mit Datenbank verbinden
psql -d legal_mcp

# In psql: Tabellen anzeigen
\dt

# Extensions prüfen
\dx
```

### Datenbank löschen (falls nötig)
```bash
psql -d postgres -c "DROP DATABASE legal_mcp;"
```

## Migrationen

### Migrationen ausführen
```bash
# Aus dem store Verzeichnis
cd store
uv run alembic upgrade head
cd ..
```

### Migration-Status prüfen
```bash
cd store
uv run alembic current
uv run alembic history
cd ..
```

### Neue Migration erstellen
```bash
cd store
uv run alembic revision --autogenerate -m "Description of changes"
cd ..
```

## API Server

### API starten
```bash
# Aus dem Projektroot (empfohlen)
uv run python run_api.py

# API läuft auf: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### API testen
```bash
# Health Check
curl http://localhost:8000/health

# API Docs im Browser
open http://localhost:8000/docs
```

### Laufenden API-Prozess beenden
```bash
# Port 8000 freigeben
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
```

## CLI Commands

### Katalog anzeigen
```bash
# Liste aller verfügbaren legal codes
uv run legal-mcp list catalog

# Bereits importierte codes
uv run legal-mcp list imported
```

### Legal Code importieren
```bash
# Kleines Beispiel zum Testen
uv run legal-mcp import --code rag_1

# BGB importieren (dauert länger)
uv run legal-mcp import --code bgb

# StGB (Strafgesetzbuch)
uv run legal-mcp import --code stgb

# Grundgesetz
uv run legal-mcp import --code gg
```

### Abfragen
```bash
# Spezifischen Paragraphen abfragen
uv run legal-mcp query --code bgb --section "§ 433"

# Mit Unterabschnitt
uv run legal-mcp query --code bgb --section "§ 433" --subsection "Abs. 1"

# JSON Output
uv run legal-mcp query --code bgb --section "§ 433" --json
```

### Semantische Suche
```bash
# Suche mit Similarity Score
uv run legal-mcp search --code bgb --query "Kaufvertrag"

# Limit setzen
uv run legal-mcp search --code bgb --query "Kaufvertrag" --limit 10

# JSON Output
uv run legal-mcp search --code bgb --query "Kaufvertrag" --json
```

## Dependencies & Environment

### Dependencies installieren/aktualisieren
```bash
# Alle Dependencies syncen
uv sync

# Neue Dependency hinzufügen
uv add package-name

# Dev-Dependency hinzufügen
uv add --dev package-name
```

### Environment prüfen
```bash
# Installierte Pakete
uv pip list

# Python Version
uv run python --version

# Virtual Environment Location
echo $VIRTUAL_ENV
```

## Ollama

### Ollama Status prüfen
```bash
# Ollama API testen
curl http://localhost:11434/api/tags

# Installierte Modelle
ollama list

# Model Pull (erforderlich!)
ollama pull ryanshillington/Qwen3-Embedding-4B:latest
```

### Ollama starten (falls nicht laufend)
```bash
ollama serve
```

## Tests

### Tests ausführen
```bash
# Alle Tests
uv run pytest

# Spezifische Test-Datei
uv run pytest tests/cli/test_import_cmd.py

# Mit Coverage
uv run pytest --cov=cli --cov=store

# Verbose Output
uv run pytest -v
```

## Git (falls relevant)

### Status prüfen
```bash
git status

# Änderungen anzeigen
git diff
```

## Troubleshooting

### Port bereits belegt
```bash
# Prozess auf Port finden und beenden
lsof -ti :8000 | xargs kill -9
```

### PostgreSQL Connection Fehler
```bash
# PostgreSQL Status prüfen
pg_isready

# PostgreSQL neu starten (macOS mit Homebrew)
brew services restart postgresql@14
```

### .env nicht gefunden
```bash
# .env existiert prüfen
ls -la .env
ls -la store/.env

# Falls nicht vorhanden
cp .env.example .env
cp .env .env store/
```

### Module nicht gefunden
```bash
# Dependencies neu syncen
uv sync

# Cache löschen und neu installieren
rm -rf .venv
uv sync
```

## Nützliche Shortcuts

### Kompletter Neustart
```bash
# 1. API beenden
lsof -ti :8000 | xargs kill -9 2>/dev/null || true

# 2. Datenbank zurücksetzen (optional)
psql -d postgres -c "DROP DATABASE IF EXISTS legal_mcp;"
psql -d postgres -c "CREATE DATABASE legal_mcp;"
psql -d legal_mcp -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 3. Migrationen
cd store && uv run alembic upgrade head && cd ..

# 4. API starten
uv run python run_api.py
```

### Quick Start (nach Setup)
```bash
# Terminal 1: API starten
uv run python run_api.py

# Terminal 2: Import
uv run legal-mcp import --code bgb

# Terminal 3: Query
uv run legal-mcp search --code bgb --query "Kaufvertrag"
```
