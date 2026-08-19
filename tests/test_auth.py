from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app
from tests.conftest import TEST_AGENT_API_KEY


REQUEST_BODY = '{"input":"Resume el perfil profesional de Mario."}'


def test_valid_bearer_token_is_accepted(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/v1/responses",
        content=REQUEST_BODY,
        headers={**auth_headers, "Content-Type": "application/json"},
    )

    assert response.status_code == 200


def test_json_content_type_with_charset_is_accepted(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/v1/responses",
        content=REQUEST_BODY,
        headers={
            **auth_headers,
            "Content-Type": "application/json; charset=utf-8",
        },
    )

    assert response.status_code == 200


def test_missing_authorization_returns_401(client: TestClient) -> None:
    response = client.post(
        "/v1/responses",
        content=REQUEST_BODY,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json() == {"detail": "Credenciales inválidas."}


def test_invalid_bearer_token_returns_401(client: TestClient) -> None:
    invalid_key = "invalid-key-used-only-by-the-test"
    response = client.post(
        "/v1/responses",
        content=REQUEST_BODY,
        headers={
            "Authorization": f"Bearer {invalid_key}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert invalid_key not in response.text
    assert TEST_AGENT_API_KEY not in response.text


def test_non_bearer_scheme_returns_401(client: TestClient) -> None:
    response = client.post(
        "/v1/responses",
        content=REQUEST_BODY,
        headers={
            "Authorization": f"Basic {TEST_AGENT_API_KEY}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_unsupported_content_type_returns_415(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/v1/responses",
        content=REQUEST_BODY,
        headers={**auth_headers, "Content-Type": "text/plain"},
    )

    assert response.status_code == 415
    assert response.json() == {"detail": "Content-Type debe ser application/json."}


def test_missing_content_type_returns_415(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/v1/responses",
        content=REQUEST_BODY,
        headers=auth_headers,
    )

    assert response.status_code == 415


def test_missing_server_key_returns_safe_503(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        _env_file=None,
        agent_api_key=None,
    )

    response = client.post(
        "/v1/responses",
        content=REQUEST_BODY,
        headers={**auth_headers, "Content-Type": "application/json"},
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "El servicio no está configurado correctamente."
    }


def test_health_remains_public(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
