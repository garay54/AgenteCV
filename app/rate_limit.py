"""Rate limiting de entrada para el endpoint autenticado del agente."""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Callable
from functools import lru_cache
from hashlib import sha256
from math import ceil
from threading import Lock
from time import monotonic
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from app.auth import require_agent_access
from app.config import Settings, get_settings


class InboundRateLimitExceeded(Exception):
    """Indica cuánto debe esperar el cliente antes de reintentar."""

    def __init__(self, retry_after_seconds: int) -> None:
        self.retry_after_seconds = retry_after_seconds
        super().__init__("Inbound request rate limit exceeded")


class InMemorySlidingWindowRateLimiter:
    """Ventana deslizante segura para un proceso y una instancia."""

    def __init__(
        self,
        max_requests: int,
        window_seconds: float = 60.0,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        if max_requests < 1:
            raise ValueError("max_requests debe ser al menos 1.")
        if window_seconds <= 0:
            raise ValueError("window_seconds debe ser positivo.")

        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._clock = clock
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()
        self._next_cleanup = 0.0

    def check(self, key: str) -> None:
        """Registra una solicitud o lanza el rechazo correspondiente."""

        now = self._clock()
        window_start = now - self.window_seconds

        with self._lock:
            if now >= self._next_cleanup:
                self._remove_expired_keys(window_start)
                self._next_cleanup = now + self.window_seconds

            requests = self._requests[key]
            while requests and requests[0] <= window_start:
                requests.popleft()

            if len(requests) >= self.max_requests:
                retry_after = max(
                    1,
                    ceil(requests[0] + self.window_seconds - now),
                )
                raise InboundRateLimitExceeded(retry_after)

            requests.append(now)

    def _remove_expired_keys(self, window_start: float) -> None:
        for key in tuple(self._requests):
            requests = self._requests[key]
            while requests and requests[0] <= window_start:
                requests.popleft()
            if not requests:
                del self._requests[key]


@lru_cache(maxsize=8)
def _build_rate_limiter(
    max_requests: int,
    window_seconds: float,
) -> InMemorySlidingWindowRateLimiter:
    return InMemorySlidingWindowRateLimiter(
        max_requests=max_requests,
        window_seconds=window_seconds,
    )


def get_rate_limiter(
    settings: Annotated[Settings, Depends(get_settings)],
) -> InMemorySlidingWindowRateLimiter:
    """Comparte el contador entre solicitudes del mismo proceso."""

    return _build_rate_limiter(
        settings.rate_limit_requests_per_minute,
        60.0,
    )


def _credential_key(request: Request) -> str:
    authorization = request.headers.get("authorization", "")
    _, _, token = authorization.partition(" ")
    token_digest = sha256(token.encode("utf-8")).hexdigest()
    return f"token:{token_digest}"


def enforce_rate_limit(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    limiter: Annotated[
        InMemorySlidingWindowRateLimiter,
        Depends(get_rate_limiter),
    ],
    _: Annotated[None, Depends(require_agent_access)],
) -> None:
    """Autentica primero y limita después sin conservar el Bearer real."""

    if not settings.rate_limit_enabled:
        return

    try:
        limiter.check(_credential_key(request))
    except InboundRateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Límite de peticiones excedido. Intenta nuevamente más tarde.",
            headers={"Retry-After": str(exc.retry_after_seconds)},
        ) from exc
