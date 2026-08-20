from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_agent_service
from app.llm import GenerationConfigurationError
from app.main import app
from app.observability import HTTP_ERRORS
from app.rate_limit import (
    InboundRateLimitExceeded,
    InMemorySlidingWindowRateLimiter,
    get_rate_limiter,
)


class _CountingUnavailableAgent:
    def __init__(self) -> None:
        self.calls = 0

    def answer(self, request):
        self.calls += 1
        raise GenerationConfigurationError("fallo simulado")


def test_sliding_window_expires_old_requests() -> None:
    current_time = [100.0]
    limiter = InMemorySlidingWindowRateLimiter(
        max_requests=2,
        window_seconds=60,
        clock=lambda: current_time[0],
    )

    limiter.check("client-a")
    limiter.check("client-a")

    with pytest.raises(InboundRateLimitExceeded) as captured:
        limiter.check("client-a")

    assert captured.value.retry_after_seconds == 60

    current_time[0] = 160.01
    limiter.check("client-a")


def test_rate_limit_is_independent_per_key() -> None:
    limiter = InMemorySlidingWindowRateLimiter(
        max_requests=1,
        clock=lambda: 100.0,
    )

    limiter.check("client-a")
    limiter.check("client-b")

    with pytest.raises(InboundRateLimitExceeded):
        limiter.check("client-a")


def test_concurrent_checks_do_not_exceed_limit() -> None:
    limiter = InMemorySlidingWindowRateLimiter(
        max_requests=5,
        clock=lambda: 100.0,
    )

    def attempt() -> bool:
        try:
            limiter.check("shared-client")
        except InboundRateLimitExceeded:
            return False
        return True

    with ThreadPoolExecutor(max_workers=20) as executor:
        accepted = list(executor.map(lambda _: attempt(), range(20)))

    assert sum(accepted) == 5


def test_endpoint_returns_429_before_third_agent_call(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    limiter = InMemorySlidingWindowRateLimiter(
        max_requests=2,
        clock=lambda: 100.0,
    )
    agent = _CountingUnavailableAgent()
    app.dependency_overrides[get_rate_limiter] = lambda: limiter
    app.dependency_overrides[get_agent_service] = lambda: agent

    errors_before = float(
        HTTP_ERRORS.labels(status_code="429", category="rate_limit")._value.get()
    )
    try:
        responses = [
            client.post(
                "/v1/responses",
                json={"input": "Resume el perfil profesional de Mario."},
                headers=auth_headers,
            )
            for _ in range(3)
        ]
    finally:
        app.dependency_overrides.pop(get_rate_limiter, None)
        app.dependency_overrides.pop(get_agent_service, None)

    assert [response.status_code for response in responses] == [503, 503, 429]
    assert responses[-1].headers["retry-after"] == "60"
    assert responses[-1].json() == {
        "detail": "Límite de peticiones excedido. Intenta nuevamente más tarde."
    }
    assert agent.calls == 2
    assert (
        float(HTTP_ERRORS.labels(status_code="429", category="rate_limit")._value.get())
        == errors_before + 1
    )
