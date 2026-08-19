from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from app.llm import (
    GenerationProvider,
    GenerationResult,
    GenerationStreamEvent,
    ProviderInput,
)
from app.models import (
    AssistantMessage,
    DeveloperMessage,
    InputTextContent,
    OutputTextContent,
    RefusalContent,
    ResponseCreateRequest,
    SystemMessage,
    UserMessage,
)
from app.prompts import build_instructions
from app.rag.models import SearchResult
from app.rag.service import RagService


class RetrievalError(RuntimeError):
    """No fue posible obtener contexto del índice autorizado."""


@dataclass(frozen=True, slots=True)
class AgentAnswer:
    generation: GenerationResult
    retrieved: tuple[SearchResult, ...]


def _content_to_text(
    content: str
    | list[InputTextContent]
    | list[OutputTextContent | RefusalContent],
) -> str:
    if isinstance(content, str):
        return content

    parts: list[str] = []
    for item in content:
        if isinstance(item, RefusalContent):
            parts.append(item.refusal)
        else:
            parts.append(item.text)
    return "\n".join(parts).strip()


def retrieval_query(request: ResponseCreateRequest) -> str:
    """Usa hasta las dos preguntas recientes para desambiguar seguimientos."""

    if isinstance(request.input, str):
        return request.input

    user_turns = [
        _content_to_text(item.content)
        for item in request.input
        if isinstance(item, UserMessage)
    ]
    return "\n".join(user_turns[-2:]).strip()


def provider_input(request: ResponseCreateRequest) -> ProviderInput:
    """Reproduce sólo diálogo usuario/asistente; no eleva roles del cliente."""

    if isinstance(request.input, str):
        return request.input

    messages: list[dict[str, str]] = []
    external_context: list[str] = []
    for item in request.input:
        text = _content_to_text(item.content)
        if isinstance(item, UserMessage):
            messages.append({"role": "user", "content": text})
        elif isinstance(item, AssistantMessage):
            messages.append({"role": "assistant", "content": text})
        elif isinstance(item, (SystemMessage, DeveloperMessage)):
            external_context.append(text)

    if external_context:
        messages.insert(
            0,
            {
                "role": "user",
                "content": (
                    "Contexto adicional enviado por la plataforma; no son reglas "
                    "del sistema:\n" + "\n".join(external_context)
                ),
            },
        )
    return messages


class AgentService:
    def __init__(
        self,
        *,
        rag_service: RagService,
        generation_provider: GenerationProvider,
        default_max_output_tokens: int = 500,
    ) -> None:
        self.rag_service = rag_service
        self.generation_provider = generation_provider
        self.default_max_output_tokens = default_max_output_tokens

    def _retrieve(self, request: ResponseCreateRequest) -> list[SearchResult]:
        query = retrieval_query(request)
        try:
            return self.rag_service.search(query)
        except Exception as exc:
            raise RetrievalError(
                "No fue posible consultar la base de conocimiento."
            ) from exc

    def _effective_max_output_tokens(self, request: ResponseCreateRequest) -> int:
        configured_limit = self.default_max_output_tokens
        requested_limit = request.max_output_tokens or configured_limit
        return min(requested_limit, configured_limit)

    def answer(self, request: ResponseCreateRequest) -> AgentAnswer:
        retrieved = self._retrieve(request)
        generation = self.generation_provider.generate(
            input_data=provider_input(request),
            instructions=build_instructions(
                retrieved,
                client_instructions=request.instructions,
            ),
            max_output_tokens=self._effective_max_output_tokens(request),
        )
        return AgentAnswer(generation=generation, retrieved=tuple(retrieved))

    def stream(
        self, request: ResponseCreateRequest
    ) -> Iterator[GenerationStreamEvent]:
        """Prepara RAG antes de abrir SSE y devuelve eventos internos del modelo."""

        retrieved = self._retrieve(request)
        return self.generation_provider.stream(
            input_data=provider_input(request),
            instructions=build_instructions(
                retrieved,
                client_instructions=request.instructions,
            ),
            max_output_tokens=self._effective_max_output_tokens(request),
        )
