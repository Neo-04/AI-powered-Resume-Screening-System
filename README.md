# AI-Powered Resume Screening System

A production-structured application for screening and matching resumes
against job descriptions. This repository currently contains the
**project skeleton** only — clean architecture layout, tooling, and
infrastructure config are in place, but feature logic has not yet been
implemented.

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL
- **Frontend**: React (Vite)
- **Infrastructure**: Docker, Docker Compose, GitHub Actions

## Project Structure

```
AI-powered-Resume-Screening-System/
├── backend/                # FastAPI app (Clean Architecture)
│   ├── app/
│   │   ├── api/            # Routers / presentation layer
│   │   ├── core/            # Settings & configuration
│   │   ├── services/         # Business logic / use cases
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── database/         # DB engine & session
│   │   ├── utils/             # Shared helpers
│   │   └── main.py            # FastAPI app entrypoint
│   ├── alembic/                # DB migrations
│   ├── tests/                  # Pytest test suite
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/                # React + Vite app
│   ├── public/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── Dockerfile
│
├── data/                     # Local dev data (gitignored contents)
│   ├── resumes/
│   ├── job_descriptions/
│   └── processed/
│
├── notebooks/                 # Exploratory / experimentation notebooks
├── docker/                     # Supporting infra config (Nginx, Postgres init)
├── docs/                        # Architecture & API documentation
├── .github/workflows/            # CI pipelines
├── docker-compose.yml
├── .env.example
├── .gitignore
└── LICENSE
```

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate    # on Windows
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Full stack with Docker Compose

```bash
cp .env.example .env
cp backend/.env.example backend/.env
docker compose up --build
```

- Backend API: http://localhost:8000 (docs at `/docs`)
- Frontend: http://localhost:5173

## Documentation

See [docs/architecture.md](docs/architecture.md) for an overview of the
clean architecture layout and [docs/api.md](docs/api.md) for API
documentation pointers.
