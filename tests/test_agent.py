from app.agent import AgentService, provider_input, retrieval_query
from app.llm import GenerationResult, GenerationUsage
from app.models import ResponseCreateRequest
from app.rag.models import KnowledgeChunk, SearchResult


class _RagStub:
    def __init__(self) -> None:
        self.query = ""

    def search(self, query: str):
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

    def generate(self, **kwargs):
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
