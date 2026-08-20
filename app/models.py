"""Modelos Pydantic del contrato Open Responses usado por el agente.

El protocolo completo admite herramientas, archivos, imágenes y otros tipos de
items. El MVP del agente es de texto, por lo que este módulo modela de forma
estricta los mensajes de texto que la plataforma cliente puede reproducir en cada solicitud.
Los campos de nivel superior se mantienen cercanos a Open Responses para que la
capa HTTP no dependa del formato particular del proveedor de IA.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator


# Límites operativos del subconjunto conversacional. El middleware HTTP impone
# además un límite total en bytes antes de deserializar el cuerpo.
MAX_TEXT_LENGTH = 16_384
MAX_TOTAL_TEXT_LENGTH = 65_536
MAX_INPUT_ITEMS = 50
MAX_CONTENT_PARTS = 20

TextValue = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=MAX_TEXT_LENGTH,
    ),
]
Identifier = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
MetadataKey = Annotated[str, StringConstraints(min_length=1, max_length=64)]
MetadataValue = Annotated[str, StringConstraints(max_length=512)]


class StrictContractModel(BaseModel):
    """
    Base para objetos cuyo contenido debe coincidir con el contrato.
    """

    model_config = ConfigDict(extra="forbid")


class InputTextContent(StrictContractModel):
    """
    Fragmento de texto enviado por una persona o por instrucciones.
    """

    type: Literal["input_text"]
    text: TextValue


class OutputTextContent(StrictContractModel):
    """
    Texto generado previamente por el agente o devuelto en la respuesta.
    """

    type: Literal["output_text"]
    text: TextValue
    annotations: list[dict[str, Any]] = Field(default_factory=list)


class RefusalContent(StrictContractModel):
    """
    Contenido con el que el agente rechazó una solicitud previa.
    """

    type: Literal["refusal"]
    refusal: TextValue


InputTextParts = Annotated[
    list[InputTextContent],
    Field(min_length=1, max_length=MAX_CONTENT_PARTS),
]
AssistantTextParts = Annotated[
    list[OutputTextContent | RefusalContent],
    Field(min_length=1, max_length=MAX_CONTENT_PARTS),
]


class UserMessage(StrictContractModel):
    """
    Mensaje de usuario dentro de la transcripción reproducida por el front.
    """

    type: Literal["message"]
    role: Literal["user"]
    content: TextValue | InputTextParts
    id: Identifier | None = None
    status: str | None = None


class SystemMessage(StrictContractModel):
    """
    Instrucción de sistema incluida como item de entrada.
    """

    type: Literal["message"]
    role: Literal["system"]
    content: TextValue | InputTextParts
    id: Identifier | None = None
    status: str | None = None


class DeveloperMessage(StrictContractModel):
    """
    Instrucción de desarrollador incluida como item de entrada.
    """

    type: Literal["message"]
    role: Literal["developer"]
    content: TextValue | InputTextParts
    id: Identifier | None = None
    status: str | None = None


class AssistantMessage(StrictContractModel):
    """
    Respuesta anterior que el front reenvía para conservar el contexto.
    """

    type: Literal["message"]
    role: Literal["assistant"]
    content: TextValue | AssistantTextParts
    id: Identifier | None = None
    phase: Literal["commentary", "final_answer"] | None = None
    status: str | None = None


# Todos los mensajes comparten type="message"; por eso el discriminador correcto
# para esta unión es role.
InputMessage = Annotated[
    UserMessage | SystemMessage | DeveloperMessage | AssistantMessage,
    Field(discriminator="role"),
]
InputItems = Annotated[
    list[InputMessage],
    Field(min_length=1, max_length=MAX_INPUT_ITEMS),
]


class ReasoningConfig(StrictContractModel):
    """
    Parámetros opcionales de razonamiento aceptados por Open Responses.
    """

    effort: Literal["none", "low", "medium", "high", "xhigh", "max"] | None = None
    summary: Literal["concise", "detailed", "auto"] | None = None


class StreamOptions(StrictContractModel):
    """
    Opciones que sólo tienen efecto cuando stream es verdadero.
    """

    include_obfuscation: bool | None = None


class TextFormat(StrictContractModel):
    """
    Formato de salida de texto soportado por el MVP.
    """

    type: Literal["text"] = "text"


class TextConfig(StrictContractModel):
    """
    Configuración opcional de la salida textual.
    """

    format: TextFormat | None = None
    verbosity: Literal["low", "medium", "high"] | None = None


Metadata = Annotated[dict[MetadataKey, MetadataValue], Field(max_length=16)]


class ResponseCreateRequest(BaseModel):
    """Solicitud que recibirá ``POST /v1/responses``.

    Open Responses permite ``input`` nulo en escenarios con estado. Este agente
    es stateless y recibe la transcripción completa, por lo que el MVP exige una
    entrada de texto no vacía en cada llamada.

    Los campos adicionales se conservan para que los parámetros configurables
    enviados por el front no sean descartados antes de llegar al adaptador.
    """

    model_config = ConfigDict(extra="allow")

    input: TextValue | InputItems
    model: Identifier | None = None
    instructions: TextValue | None = None
    previous_response_id: Identifier | None = None
    include: list[
        Literal["reasoning.encrypted_content", "message.output_text.logprobs"]
    ] | None = None
    tools: list[dict[str, Any]] | None = None
    tool_choice: str | dict[str, Any] | None = None
    metadata: Metadata | None = None
    text: TextConfig | None = None
    temperature: float | None = Field(default=None, ge=0, le=2)
    top_p: float | None = Field(default=None, ge=0, le=1)
    presence_penalty: float | None = None
    frequency_penalty: float | None = None
    parallel_tool_calls: bool | None = None
    stream: bool = False
    stream_options: StreamOptions | None = None
    background: bool = False
    max_output_tokens: int | None = Field(default=None, ge=16)
    max_tool_calls: int | None = Field(default=None, ge=1)
    reasoning: ReasoningConfig | None = None
    safety_identifier: Annotated[str, StringConstraints(max_length=64)] | None = None
    prompt_cache_key: Annotated[str, StringConstraints(max_length=64)] | None = None
    truncation: Literal["auto", "disabled"] = "disabled"
    store: bool = False
    service_tier: Literal["auto", "default", "flex", "priority"] = "default"
    top_logprobs: int | None = Field(default=None, ge=0, le=20)

    @model_validator(mode="after")
    def validate_total_text_length(self) -> ResponseCreateRequest:
        """Impide eludir el límite repartiendo texto entre muchos mensajes."""

        total_length = len(self.instructions or "")

        if isinstance(self.input, str):
            total_length += len(self.input)
        else:
            for message in self.input:
                if isinstance(message.content, str):
                    total_length += len(message.content)
                    continue

                for part in message.content:
                    if isinstance(part, RefusalContent):
                        total_length += len(part.refusal)
                    else:
                        total_length += len(part.text)

        if total_length > MAX_TOTAL_TEXT_LENGTH:
            raise ValueError(
                "La suma del texto de entrada e instrucciones excede "
                f"{MAX_TOTAL_TEXT_LENGTH} caracteres."
            )

        return self


class ResponseOutputMessage(StrictContractModel):
    """
    Mensaje de asistente incluido en ``ResponseResource.output``.
    """

    id: Identifier
    type: Literal["message"] = "message"
    status: Literal["in_progress", "completed", "incomplete"]
    role: Literal["assistant"] = "assistant"
    content: AssistantTextParts


class IncompleteDetails(StrictContractModel):
    """
    Explica por qué una respuesta terminó incompleta.
    """

    reason: str


class GenerationError(StrictContractModel):
    """
    Error producido durante la generación de una respuesta.
    """

    code: str
    message: str


class InputTokenDetails(StrictContractModel):
    """
    Desglose del consumo de tokens de entrada.
    """

    cached_tokens: int = Field(default=0, ge=0)


class OutputTokenDetails(StrictContractModel):
    """
    Desglose del consumo de tokens de salida.
    """

    reasoning_tokens: int = Field(default=0, ge=0)


class ResponseUsage(StrictContractModel):
    """
    Consumo de tokens reportado por el proveedor de IA.
    """

    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)
    input_tokens_details: InputTokenDetails
    output_tokens_details: OutputTokenDetails


class ResponseReasoning(StrictContractModel):
    """
    Configuración de razonamiento reflejada en la respuesta.
    """

    effort: Literal["none", "low", "medium", "high", "xhigh", "max"] | None
    summary: Literal["concise", "detailed", "auto"] | None


class ResponseText(StrictContractModel):
    """
    Configuración textual reflejada en la respuesta final.
    """

    format: TextFormat
    verbosity: Literal["low", "medium", "high"] | None = None


class ResponseResource(StrictContractModel):
    """
    Respuesta completa no streaming compatible con el MVP.
    """

    id: Identifier
    object: Literal["response"] = "response"
    created_at: int = Field(ge=0)
    completed_at: int | None
    status: Literal[
        "completed", "failed", "in_progress", "cancelled", "queued", "incomplete"
    ]
    incomplete_details: IncompleteDetails | None
    model: str
    previous_response_id: str | None
    instructions: str | None
    output: list[ResponseOutputMessage]
    error: GenerationError | None
    tools: list[dict[str, Any]]
    tool_choice: str | dict[str, Any]
    truncation: Literal["auto", "disabled"]
    parallel_tool_calls: bool
    text: ResponseText
    top_p: float
    presence_penalty: float
    frequency_penalty: float
    top_logprobs: int
    temperature: float
    reasoning: ResponseReasoning | None
    usage: ResponseUsage | None
    max_output_tokens: int | None
    max_tool_calls: int | None
    store: bool
    background: bool
    service_tier: str
    metadata: dict[str, str]
    safety_identifier: str | None
    prompt_cache_key: str | None


class ErrorDetail(StrictContractModel):
    """
    Detalle seguro y estable de un error HTTP del agente.
    """

    message: str
    type: str
    param: str | None = None
    code: str


class ErrorResponse(StrictContractModel):
    """
    Envoltura uniforme para errores que no son respuestas del modelo.
    """

    error: ErrorDetail
