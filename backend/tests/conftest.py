import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture()
def client() -> TestClient:
    """Provide a FastAPI TestClient for use in tests."""
    return TestClient(app)
