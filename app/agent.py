from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterator
from dataclasses import dataclass
from time import time
from uuid import uuid4

from app.llm import (
    GenerationProvider,
    GenerationResult,
    GenerationStreamCompleted,
    GenerationStreamEvent,
    GenerationStreamStarted,
    GenerationTextDelta,
    GenerationUsage,
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


OUT_OF_SCOPE_MESSAGE = (
    "No puedo realizar esa tarea. Sólo puedo responder preguntas sobre el perfil, "
    "la formación, la experiencia, las habilidades, los proyectos, la investigación "
    "y las publicaciones profesionales de Mario."
)

_TASK_ACTION_RE = re.compile(
    r"\b(escribe|genera|crea|haz|dame|proporciona|muestra|implementa|"
    r"calcula|resuelve|traduce|quiero|necesito|puedes|podrias|pide|solicita)\b"
)
_TASK_ARTIFACT_RE = re.compile(
    r"\b(codigo|programa|script|funcion|algoritmo|suma|promedio|"
    r"traduccion|poema|receta)\b"
)
_PROFESSIONAL_SCOPE_RE = re.compile(
    r"\b(mario|agentecv|rankvideo|curriculum|perfil profesional|trayectoria|"
    r"tesis|doctorado|maestria)\b"
)
_AMBIGUOUS_EDUCATION_RE = re.compile(
    r"\b(otros? grados?|otros? estudios?|que mas estudio|ademas del doctorado)\b"
)


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


def _normalized_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )


def _user_turns(request: ResponseCreateRequest) -> list[str]:
    if isinstance(request.input, str):
        return [request.input]
    return [
        _content_to_text(item.content)
        for item in request.input
        if isinstance(item, UserMessage)
    ]


def is_obvious_out_of_scope(request: ResponseCreateRequest) -> bool:
    """Rechaza entregables generales evidentes sin invocar RAG ni el modelo."""

    turns = _user_turns(request)
    if not turns:
        return False
    latest = _normalized_text(turns[-1])
    return bool(
        _TASK_ACTION_RE.search(latest)
        and _TASK_ARTIFACT_RE.search(latest)
        and not _PROFESSIONAL_SCOPE_RE.search(latest)
    )


def retrieval_query(request: ResponseCreateRequest) -> str:
    """Usa hasta las dos preguntas recientes para desambiguar seguimientos."""

    user_turns = _user_turns(request)
    query = "\n".join(user_turns[-2:]).strip()
    if user_turns and _AMBIGUOUS_EDUCATION_RE.search(
        _normalized_text(user_turns[-1])
    ):
        query += (
            "\nTema de recuperación: formación académica completa de Mario, "
            "incluidas licenciatura, maestría y doctorado."
        )
    return query


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

    def _policy_refusal(self, request: ResponseCreateRequest) -> GenerationResult | None:
        if not is_obvious_out_of_scope(request):
            return None
        timestamp = int(time())
        return GenerationResult(
            id=f"resp_{uuid4().hex}",
            text=OUT_OF_SCOPE_MESSAGE,
            model=self.generation_provider.model_name,
            created_at=timestamp,
            completed_at=timestamp,
            status="completed",
            usage=GenerationUsage(),
        )

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
        refusal = self._policy_refusal(request)
        if refusal is not None:
            return AgentAnswer(generation=refusal, retrieved=())

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

        refusal = self._policy_refusal(request)
        if refusal is not None:
            return iter(
                (
                    GenerationStreamStarted(
                        id=refusal.id,
                        model=refusal.model,
                        created_at=refusal.created_at,
                    ),
                    GenerationTextDelta(delta=refusal.text),
                    GenerationStreamCompleted(result=refusal),
                )
            )

        retrieved = self._retrieve(request)
        return self.generation_provider.stream(
            input_data=provider_input(request),
            instructions=build_instructions(
                retrieved,
                client_instructions=request.instructions,
            ),
            max_output_tokens=self._effective_max_output_tokens(request),
        )
