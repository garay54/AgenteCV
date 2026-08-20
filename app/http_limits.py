"""Límites HTTP aplicados antes de validar el contrato de la API."""

from __future__ import annotations

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class _RequestBodyTooLarge(Exception):
    """Señal interna emitida cuando un cuerpo fragmentado excede el límite."""


class RequestBodyLimitMiddleware:
    """Rechaza cuerpos grandes aun si no incluyen ``Content-Length``."""

    def __init__(self, app: ASGIApp, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if (
            scope["type"] != "http"
            or scope["method"] != "POST"
            or scope["path"] != "/v1/responses"
        ):
            await self.app(scope, receive, send)
            return

        content_length = dict(scope.get("headers", [])).get(b"content-length")
        if content_length is not None:
            try:
                declared_size = int(content_length)
            except ValueError:
                declared_size = 0

            if declared_size > self.max_bytes:
                await self._send_too_large(scope, receive, send)
                return

        received_bytes = 0

        async def limited_receive() -> Message:
            nonlocal received_bytes

            message = await receive()
            if message["type"] == "http.request":
                received_bytes += len(message.get("body", b""))
                if received_bytes > self.max_bytes:
                    raise _RequestBodyTooLarge
            return message

        try:
            await self.app(scope, limited_receive, send)
        except _RequestBodyTooLarge:
            await self._send_too_large(scope, receive, send)

    async def _send_too_large(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        response = JSONResponse(
            status_code=413,
            content={
                "detail": "El cuerpo de la solicitud excede el límite permitido."
            },
        )
        await response(scope, receive, send)
