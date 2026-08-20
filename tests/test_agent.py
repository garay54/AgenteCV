from app.agent import AgentService, OUT_OF_SCOPE_MESSAGE, provider_input, retrieval_query
from app.llm import (
    GenerationResult,
    GenerationStreamCompleted,
    GenerationStreamStarted,
    GenerationTextDelta,
    GenerationUsage,
)
from app.models import ResponseCreateRequest
from app.rag.models import KnowledgeChunk, SearchResult


class _RagStub:
    def __init__(self) -> None:
        self.query = ""
        self.calls = 0

    def search(self, query: str):
        self.calls += 1
        self.query = query
        return [
            SearchResult(
                chunk=KnowledgeChunk(
                    id="chunk-1",
                    text="Mario desarrolló un sistema de evaluación de pavimentos.",
                    metadata={
                        "document": "research.md",
                        "section_path": "Tesis doctoral > Sistema propuesto",
                        "source_ids": "SRC-TD-01",
                    },
                ),
                score=0.9,
                distance=0.1,
            )
        ]


class _GenerationStub:
    model_name = "gpt-5.6-luna"

    def __init__(self) -> None:
        self.arguments = {}
        self.calls = 0

    def generate(self, **kwargs):
        self.calls += 1
        self.arguments = kwargs
        return GenerationResult(
            id="resp-test",
            text="Respuesta fundamentada.",
            model=self.model_name,
            created_at=1,
            completed_at=2,
            status="completed",
            usage=GenerationUsage(),
        )

    def stream(self, **kwargs):
        self.calls += 1
        self.arguments = kwargs
        return iter(())


def test_multiturn_query_uses_two_recent_user_turns() -> None:
    request = ResponseCreateRequest.model_validate(
        {
            "input": [
                {"type": "message", "role": "user", "content": "Háblame del doctorado."},
                {
                    "type": "message",
                    "role": "assistant",
                    "content": "Mario desarrolló un sistema de evaluación.",
                },
                {
                    "type": "message",
                    "role": "user",
                    "content": "¿Qué tecnologías utilizó ahí?",
                },
            ]
        }
    )

    assert retrieval_query(request) == (
        "Háblame del doctorado.\n¿Qué tecnologías utilizó ahí?"
    )
    assert provider_input(request)[-1] == {
        "role": "user",
        "content": "¿Qué tecnologías utilizó ahí?",
    }


def test_ambiguous_education_followup_expands_retrieval_topic() -> None:
    request = ResponseCreateRequest.model_validate(
        {
            "input": [
                {
                    "type": "message",
                    "role": "user",
                    "content": "¿Cuándo obtuvo Mario el doctorado?",
                },
                {
                    "type": "message",
                    "role": "assistant",
                    "content": "Obtuvo el grado el 10 de agosto de 2026.",
                },
                {
                    "type": "message",
                    "role": "user",
                    "content": "¿Tenía otros grados?",
                },
            ]
        }
    )

    query = retrieval_query(request)

    assert "¿Cuándo obtuvo Mario el doctorado?" in query
    assert "¿Tenía otros grados?" in query
    assert "licenciatura, maestría y doctorado" in query


def test_agent_connects_retrieval_prompt_and_generation() -> None:
    rag = _RagStub()
    generation = _GenerationStub()
    service = AgentService(
        rag_service=rag,
        generation_provider=generation,
        default_max_output_tokens=300,
    )
    request = ResponseCreateRequest.model_validate(
        {
            "input": "¿Qué desarrolló Mario durante el doctorado?",
            "instructions": "Responde brevemente.",
            "max_output_tokens": 900,
        }
    )

    answer = service.answer(request)

    assert rag.query == "¿Qué desarrolló Mario durante el doctorado?"
    assert answer.generation.text == "Respuesta fundamentada."
    assert generation.arguments["input_data"] == request.input
    assert generation.arguments["max_output_tokens"] == 300
    assert "sistema de evaluación de pavimentos" in generation.arguments["instructions"]
    assert "SRC-TD-01" in generation.arguments["instructions"]
    assert "Responde brevemente" in generation.arguments["instructions"]
    assert "no inventes" in generation.arguments["instructions"].casefold()
    assert "generar o depurar código" in generation.arguments["instructions"]


def test_obvious_code_request_is_refused_without_rag_or_model() -> None:
    rag = _RagStub()
    generation = _GenerationStub()
    service = AgentService(
        rag_service=rag,
        generation_provider=generation,
        default_max_output_tokens=300,
    )
    request = ResponseCreateRequest.model_validate(
        {
            "input": (
                "Quiero un código que pida dos números, los sume y calcule "
                "su promedio."
            )
        }
    )

    answer = service.answer(request)

    assert answer.generation.text == OUT_OF_SCOPE_MESSAGE
    assert answer.retrieved == ()
    assert rag.calls == 0
    assert generation.calls == 0


def test_obvious_code_request_has_complete_local_stream() -> None:
    rag = _RagStub()
    generation = _GenerationStub()
    service = AgentService(
        rag_service=rag,
        generation_provider=generation,
        default_max_output_tokens=300,
    )
    request = ResponseCreateRequest.model_validate(
        {"input": "Genera un programa para sumar dos números.", "stream": True}
    )

    events = list(service.stream(request))

    assert isinstance(events[0], GenerationStreamStarted)
    assert events[1] == GenerationTextDelta(delta=OUT_OF_SCOPE_MESSAGE)
    assert isinstance(events[2], GenerationStreamCompleted)
    assert events[2].result.text == OUT_OF_SCOPE_MESSAGE
    assert rag.calls == 0
    assert generation.calls == 0
