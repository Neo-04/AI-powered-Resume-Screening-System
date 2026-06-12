# API Documentation

The backend is built with FastAPI, which automatically generates
interactive API documentation:

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI schema: `/api/v1/openapi.json`

API endpoints are versioned under the `/api/v1` prefix (configurable via
`API_V1_PREFIX` in `backend/app/core/config.py`).

Detailed endpoint documentation will be added here as features are
implemented.
