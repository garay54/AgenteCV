from types import SimpleNamespace

from app.llm import OpenAIResponsesProvider


class _ResponsesStub:
    def __init__(self) -> None:
        self.arguments = {}

    def create(self, **kwargs):
        self.arguments = kwargs
        return SimpleNamespace(
            id="resp-provider-001",
            output_text="Respuesta real simulada por el SDK.",
            model="gpt-5.6-luna",
            created_at=100,
            completed_at=101,
            status="completed",
            incomplete_details=None,
            usage=SimpleNamespace(
                input_tokens=80,
                output_tokens=20,
                total_tokens=100,
                input_tokens_details=SimpleNamespace(cached_tokens=10),
                output_tokens_details=SimpleNamespace(reasoning_tokens=0),
            ),
        )


class _OpenAIClientStub:
    def __init__(self) -> None:
        self.responses = _ResponsesStub()


def test_openai_adapter_uses_luna_responses_and_server_limits() -> None:
    client = _OpenAIClientStub()
    provider = OpenAIResponsesProvider(
        api_key=None,
        model="gpt-5.6-luna",
        reasoning_effort="none",
        text_verbosity="low",
        client=client,
    )

    result = provider.generate(
        input_data="Resume el perfil de Mario.",
        instructions="Usa sólo la fuente recuperada.",
        max_output_tokens=400,
    )

    arguments = client.responses.arguments
    assert arguments["model"] == "gpt-5.6-luna"
    assert arguments["reasoning"] == {"effort": "none"}
    assert arguments["text"] == {"verbosity": "low"}
    assert arguments["store"] is False
    assert arguments["stream"] is False
    assert arguments["max_output_tokens"] == 400
    assert result.text == "Respuesta real simulada por el SDK."
    assert result.usage.total_tokens == 100
    assert result.usage.cached_tokens == 10
