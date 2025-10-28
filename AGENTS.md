# CajaClara — AI Coding Agent Instructions

## Project Overview

CajaClara is a web application for personal and micro-business financial management, focused on young users in Medellín, Colombia. It supports manual entry and OCR-based receipt capture (OpenAI Vision API), with local storage and cloud sync.

## Architecture

- **Frontend:** React (JSX) — `/frontend/src/`
- **Backend:** FastAPI (Python 3.11+) — `/backend/app/`
- **Database:** PostgreSQL 14
- **ORM:** SQLAlchemy 2.0+ (models as Python classes)
- **OCR:** OpenAI Vision API via `/backend/app/services/ocr_service.py`

### Key Directories

- `/backend/app/models/` — SQLAlchemy models (e.g., `transaction.py`, `user.py`)
- `/backend/app/schemas/` — Pydantic schemas for API validation
- `/backend/app/routes/` — FastAPI endpoints
- `/backend/app/services/` — Business logic (e.g., OCR, transactions)
- `/frontend/src/components/` — React UI components
- `/frontend/src/services/api.js` — API client for backend

## Developer Workflow

- **Backend:**
  - Install dependencies: `uv sync`
  - Run dev server: `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
  - Migrations: `uv run alembic revision --autogenerate -m "desc"` → `uv run alembic upgrade head`
  - Tests: `uv run pytest tests/ -v`
  - Format/lint: `uv run ruff format .` and `uv run ruff check --fix .`
- **Frontend:**
  - Install: `npm install`
  - Dev server: `npm run dev`
  - Format/lint: `npm run format`, `npm run lint`

## Conventions & Patterns

- **Naming:**
  - Code: English (variables, classes, files)
  - Comments/docs: Spanish
- **Backend:**
  - Models: Python classes, PEP8, type hints, Google-style docstrings (in Spanish)
  - Error handling: Explicit with try/except and logging
  - Validation: Pydantic schemas before DB persistence
- **Frontend:**
  - Components: PascalCase
  - Functions/variables: camelCase
  - Constants: UPPER_SNAKE_CASE
  - Hooks: At top of component
  - Props: Destructured in signature

## Integration Points

- **OCR:** Use `/api/v1/ocr/process` for image receipt parsing
- **Transactions:** CRUD via `/api/v1/transactions`
- **Categories/Accounts:** CRUD via `/api/v1/categories`, `/api/v1/accounts`

## Examples

- **Backend Model:** `backend/app/models/transaction.py`
- **Frontend Component:** `frontend/src/components/FormularioManual.jsx`
- **API Client:** `frontend/src/services/api.js`

## Special Notes

- Always run `uv sync` after changing Python dependencies
- Generate Alembic migrations after changing models
- Run tests before commit
- Format code before commit
- Document public functions with docstrings (Spanish)
- Use type hints in Python
- Validate schemas before DB writes
- Handle errors explicitly

---

_Last updated: 2025-10-24_
