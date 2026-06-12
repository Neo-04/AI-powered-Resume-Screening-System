# Architecture Overview

This project follows a **Clean Architecture** approach for the backend,
separating concerns into distinct, independently testable layers.

## Backend Layers (`backend/app/`)

- **api/** — Presentation layer. FastAPI routers and request/response
  handling, grouped by version (`api/v1/`). Contains no business logic.
- **schemas/** — Data Transfer Objects (DTOs). Pydantic models used to
  validate and serialize data crossing the API boundary.
- **services/** — Application/business logic layer. Use cases that
  orchestrate models and external integrations, independent of FastAPI
  and the database.
- **models/** — Domain/persistence layer. SQLAlchemy ORM models
  representing database entities.
- **database/** — Infrastructure layer. Database engine/session setup
  and the declarative base used by models.
- **core/** — Cross-cutting configuration (settings, environment
  variables, constants).
- **utils/** — Small, shared helper functions with no business logic.

## Dependency Direction

```
api -> services -> models/database
api -> schemas
services -> schemas
```

Outer layers (API) depend on inner layers (services, models), but inner
layers do not depend on the API layer. This keeps business logic
testable and decoupled from HTTP/FastAPI specifics.

## Frontend (`frontend/`)

A standard React + Vite single-page application:

- **pages/** — Top-level route components.
- **components/** — Reusable UI components.
- **services/** — API client wrappers (e.g. Axios instance) for talking
  to the backend.

## Infrastructure

- **docker/** — Supporting configuration for containerized services
  (e.g. Nginx config for serving the frontend).
- **docker-compose.yml** — Local multi-container orchestration of the
  backend, frontend, and PostgreSQL database.
- **.github/workflows/** — CI pipelines for linting, testing, and
  building both backend and frontend.
