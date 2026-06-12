import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    """Provide a FastAPI TestClient for use in tests."""
    return TestClient(app)
