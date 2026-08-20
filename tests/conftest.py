import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.config import Settings, get_settings
from app.main import app
from app.rate_limit import InMemorySlidingWindowRateLimiter, get_rate_limiter


# Esta credencial sólo existe en la suite de pruebas y puede publicarse.
TEST_AGENT_API_KEY = "test-agent-key-not-a-real-secret"


def get_test_settings() -> Settings:
    """Crea configuración aislada sin leer el .env personal."""

    return Settings(
        _env_file=None,
        agent_api_key=SecretStr(TEST_AGENT_API_KEY),
    )


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides[get_settings] = get_test_settings
    limiter = InMemorySlidingWindowRateLimiter(
        max_requests=get_test_settings().rate_limit_requests_per_minute
    )
    app.dependency_overrides[get_rate_limiter] = lambda: limiter
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_settings, None)
    app.dependency_overrides.pop(get_rate_limiter, None)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {TEST_AGENT_API_KEY}"}
