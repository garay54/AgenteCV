from fastapi.testclient import TestClient

from app.main import MOCK_RESPONSE_TEXT, app
from app.models import ResponseResource


def test_non_streaming_response_satisfies_contract_without_model_call(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """La respuesta simulada debe validar sin red, SDK ni credenciales."""

    response = client.post(
        "/v1/responses",
        json={
            "model": "cv-agent",
            "input": [
                {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "¿Cuál es la experiencia profesional de Mario?",
                        }
                    ],
                }
            ],
            "stream": False,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    # Volver a validar la salida evita que la prueba dependa sólo de FastAPI.
    contract = ResponseResource.model_validate(response.json())
    assert contract.object == "response"
    assert contract.status == "completed"
    assert contract.model == "cv-agent"
    assert contract.id.startswith("resp_")
    assert contract.output[0].id.startswith("msg_")
    assert contract.output[0].role == "assistant"
    assert contract.output[0].content[0].type == "output_text"
    assert contract.output[0].content[0].text == MOCK_RESPONSE_TEXT
    assert contract.usage is not None
    assert contract.usage.total_tokens == 0


def test_minimal_string_request_uses_mock_model_name(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/v1/responses",
        json={"input": "Resume el perfil profesional de Mario."},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["model"] == "cv-agent-mock"


def test_streaming_is_rejected_until_sse_is_implemented(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/v1/responses",
        json={"input": "Resume el perfil profesional de Mario.", "stream": True},
        headers=auth_headers,
    )

    assert response.status_code == 501
    assert response.json() == {"detail": "El streaming SSE todavía no está implementado."}
