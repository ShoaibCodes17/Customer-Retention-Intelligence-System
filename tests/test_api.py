"""
API tests. Run with: pytest tests/
Requires the app to be importable (a running/mocked DB isn't needed for
the health check test below).
"""
import pytest
from src.api.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"
