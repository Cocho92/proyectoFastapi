# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
uv sync                          # Install dependencies
source .venv/bin/activate        # Activate virtual environment
```

### Code Quality
```bash
bash ./scripts/format.sh         # Format code with ruff
bash ./scripts/lint.sh           # Run mypy type checking and ruff linting
bash ./scripts/test.sh           # Run tests with coverage
```

### Running Tests
```bash
# Local development (with coverage)
bash ./scripts/test.sh

# In Docker container with running stack
docker compose exec backend bash scripts/tests-start.sh

# Single test with pytest arguments
docker compose exec backend bash scripts/tests-start.sh -x  # stop on first error
```

### Database Migrations
```bash
# Inside backend container
docker compose exec backend bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Development Server
```bash
# Inside container for development
docker compose exec backend bash
fastapi run --reload app/main.py
```

## Architecture

### Technology Stack
- **Framework**: FastAPI with SQLModel for ORM
- **Database**: PostgreSQL with Alembic migrations
- **Authentication**: JWT with bcrypt password hashing
- **Validation**: Pydantic models
- **Package Management**: uv

### Project Structure
- `app/models.py` - SQLModel database models and Pydantic schemas
- `app/api/routes/` - API endpoint definitions organized by feature
- `app/crud.py` - Database CRUD operations
- `app/core/` - Configuration, database, security, logging
- `app/services/` - Business logic services (Excel processing, Google Sheets)
- `app/tests/` - Test suite organized by feature

### Key Models
- **User**: Authentication and user management with items/tasks relationships
- **Item**: Basic CRUD items owned by users
- **Task**: Task management system with assignments
- **TaskAssignment**: Many-to-many relationship between users and tasks

### API Organization
Routes are modular in `app/api/routes/`:
- `login.py` - Authentication endpoints
- `users.py` - User management
- `items.py` - Item CRUD operations
- `tasks.py` - Task management
- `errores_pami.py` - PAMI error handling
- `internaciones_op.py` - Operations internment processing
- `private.py` - Development-only endpoints (local environment)

### External Integrations
- Google Sheets API via `gspread`
- Excel processing with `pandas` and `openpyxl`
- Email templates using MJML (source in `email-templates/src/`, built to `email-templates/build/`)

### Configuration
- Settings managed via Pydantic Settings from `../.env`
- Environment-specific configuration in `app/core/config.py`
- Docker Compose overrides for development in `docker-compose.override.yml`