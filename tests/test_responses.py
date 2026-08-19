from time import time

import pytest
from fastapi.testclient import TestClient

from app.agent import AgentAnswer
from app.dependencies import get_agent_service
from app.llm import GenerationRateLimitError, GenerationResult, GenerationUsage
from app.main import app
from app.models import ResponseResource


STUB_RESPONSE_TEXT = (
    "Mario cuenta con experiencia documentada en investigación y desarrollo de "
    "sistemas de inteligencia artificial."
)


class _AgentStub:
    def answer(self, request) -> AgentAnswer:
        timestamp = int(time())
        return AgentAnswer(
            generation=GenerationResult(
                id="resp_stub_001",
                text=STUB_RESPONSE_TEXT,
                model="gpt-5.6-luna",
                created_at=timestamp,
                completed_at=timestamp,
                status="completed",
                usage=GenerationUsage(
                    input_tokens=120,
                    output_tokens=24,
                    total_tokens=144,
                ),
            ),
            retrieved=(),
        )


class _RateLimitedAgentStub:
    def answer(self, request) -> AgentAnswer:
        raise GenerationRateLimitError("detalle interno no publicable")


@pytest.fixture
def generated_client(client: TestClient):
    app.dependency_overrides[get_agent_service] = lambda: _AgentStub()
    yield client
    app.dependency_overrides.pop(get_agent_service, None)


def test_non_streaming_response_satisfies_contract_without_network_call(
    generated_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = generated_client.post(
        "/v1/responses",
        json={
            "model": "modelo-no-autorizado-del-cliente",
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

    contract = ResponseResource.model_validate(response.json())
    assert contract.object == "response"
    assert contract.status == "completed"
    assert contract.model == "gpt-5.6-luna"
    assert contract.id == "resp_stub_001"
    assert contract.output[0].id.startswith("msg_")
    assert contract.output[0].role == "assistant"
    assert contract.output[0].content[0].text == STUB_RESPONSE_TEXT
    assert contract.usage is not None
    assert contract.usage.total_tokens == 144
    assert contract.reasoning is not None
    assert contract.reasoning.effort == "none"


def test_minimal_string_request_uses_configured_generation_model(
    generated_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = generated_client.post(
        "/v1/responses",
        json={"input": "Resume el perfil profesional de Mario."},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["model"] == "gpt-5.6-luna"


def test_streaming_is_rejected_until_sse_is_implemented(
    generated_client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = generated_client.post(
        "/v1/responses",
        json={"input": "Resume el perfil profesional de Mario.", "stream": True},
        headers=auth_headers,
    )

    assert response.status_code == 501
    assert response.json() == {
        "detail": "El streaming SSE todavía no está implementado."
    }


def test_provider_rate_limit_is_mapped_without_leaking_details(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    app.dependency_overrides[get_agent_service] = lambda: _RateLimitedAgentStub()
    try:
        response = client.post(
            "/v1/responses",
            json={"input": "Resume el perfil profesional de Mario."},
            headers=auth_headers,
        )
    finally:
        app.dependency_overrides.pop(get_agent_service, None)

    assert response.status_code == 429
    assert response.json() == {
        "detail": "El agente alcanzó temporalmente su límite de uso."
    }
    assert "detalle interno" not in response.text
