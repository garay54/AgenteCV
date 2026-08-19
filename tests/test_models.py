import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.models import ResponseCreateRequest, ResponseResource


def test_accepts_simple_text_input() -> None:
    request = ResponseCreateRequest.model_validate(
        {"input": "Resume la experiencia profesional de Mario."}
    )

    assert request.input == "Resume la experiencia profesional de Mario."
    assert request.stream is False
    assert request.truncation == "disabled"


def test_accepts_replayed_multiturn_transcript() -> None:
    request = ResponseCreateRequest.model_validate(
        {
            "model": "cv-agent",
            "input": [
                {
                    "type": "message",
                    "role": "user",
                    "content": "Explícame el proyecto doctoral.",
                },
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "El proyecto estudió la evaluación de pavimentos.",
                        }
                    ],
                },
                {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "¿Qué resultados obtuvo?"}
                    ],
                },
            ],
            "reasoning": {"effort": "medium"},
        }
    )

    assert isinstance(request.input, list)
    assert len(request.input) == 3
    assert request.input[1].role == "assistant"


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"input": "   "},
        {"input": []},
        {"input": [{"type": "message", "role": "invalid", "content": "Hola"}]},
        {"input": "Hola", "temperature": 3},
        {"input": "Hola", "max_output_tokens": 15},
    ],
)
def test_rejects_invalid_request_values(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        ResponseCreateRequest.model_validate(payload)


def test_malformed_json_has_a_structured_validation_error() -> None:
    with pytest.raises(ValidationError) as captured:
        ResponseCreateRequest.model_validate_json('{"input":')

    first_error = captured.value.errors()[0]
    assert first_error["type"] == "json_invalid"
    assert first_error["loc"] == ()


def test_validates_complete_non_streaming_response() -> None:
    response = ResponseResource.model_validate(
        {
            "id": "resp_test_001",
            "object": "response",
            "created_at": 1_786_987_200,
            "completed_at": 1_786_987_201,
            "status": "completed",
            "incomplete_details": None,
            "model": "cv-agent",
            "previous_response_id": None,
            "instructions": None,
            "output": [
                {
                    "id": "msg_test_001",
                    "type": "message",
                    "status": "completed",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "Mario cuenta con experiencia en inteligencia artificial.",
                            "annotations": [],
                        }
                    ],
                }
            ],
            "error": None,
            "tools": [],
            "tool_choice": "auto",
            "truncation": "disabled",
            "parallel_tool_calls": False,
            "text": {"format": {"type": "text"}},
            "top_p": 1,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "top_logprobs": 0,
            "temperature": 1,
            "reasoning": None,
            "usage": {
                "input_tokens": 10,
                "output_tokens": 8,
                "total_tokens": 18,
                "input_tokens_details": {"cached_tokens": 0},
                "output_tokens_details": {"reasoning_tokens": 0},
            },
            "max_output_tokens": None,
            "max_tool_calls": None,
            "store": False,
            "background": False,
            "service_tier": "default",
            "metadata": {},
            "safety_identifier": None,
            "prompt_cache_key": None,
        }
    )

    assert response.status == "completed"
    assert response.output[0].content[0].text.startswith("Mario")


def test_fastapi_returns_controlled_422_for_malformed_json() -> None:
    """A03 comprueba validación HTTP sin adelantar el endpoint productivo A04."""

    validation_app = FastAPI()

    @validation_app.post("/validate")
    def validate_request(payload: ResponseCreateRequest) -> dict[str, bool]:
        return {"valid": True}

    response = TestClient(validation_app).post(
        "/validate",
        content='{"input":',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    body = response.json()
    assert isinstance(body.get("detail"), list)
    assert body["detail"][0]["type"] == "json_invalid"
    # La respuesta es JSON controlado, no una traza interna de Python.
    assert "Traceback" not in json.dumps(body)
