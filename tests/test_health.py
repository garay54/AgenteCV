from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app, create_app


def test_health_endpoint() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_development_keeps_interactive_documentation() -> None:
    development_app = create_app(
        Settings(_env_file=None, app_environment="development")
    )

    with TestClient(development_app) as client:
        assert client.get("/docs").status_code == 200
        assert client.get("/redoc").status_code == 200
        assert client.get("/openapi.json").status_code == 200


def test_production_hides_documentation_and_adds_security_headers() -> None:
    production_app = create_app(
        Settings(_env_file=None, app_environment="production")
    )

    with TestClient(production_app) as client:
        assert client.get("/docs").status_code == 404
        assert client.get("/redoc").status_code == 404
        assert client.get("/openapi.json").status_code == 404
        response = client.get("/health")

    assert response.headers["strict-transport-security"] == "max-age=31536000"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["content-security-policy"] == "frame-ancestors 'none'"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
