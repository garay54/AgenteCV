from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.http_limits import RequestBodyLimitMiddleware


def _limited_client(max_bytes: int) -> TestClient:
    limited_app = FastAPI()
    limited_app.add_middleware(
        RequestBodyLimitMiddleware,
        max_bytes=max_bytes,
    )

    @limited_app.post("/v1/responses")
    async def consume_body(request: Request) -> dict[str, int]:
        body = await request.body()
        return {"received": len(body)}

    return TestClient(limited_app)


def test_body_at_http_limit_is_accepted() -> None:
    with _limited_client(max_bytes=64) as client:
        response = client.post("/v1/responses", content=b"x" * 64)

    assert response.status_code == 200
    assert response.json() == {"received": 64}


def test_declared_body_above_http_limit_returns_413() -> None:
    with _limited_client(max_bytes=64) as client:
        response = client.post("/v1/responses", content=b"x" * 65)

    assert response.status_code == 413
    assert response.json() == {
        "detail": "El cuerpo de la solicitud excede el límite permitido."
    }


def test_chunked_body_above_http_limit_returns_413() -> None:
    def body_chunks():
        yield b"x" * 40
        yield b"y" * 40

    with _limited_client(max_bytes=64) as client:
        response = client.post("/v1/responses", content=body_chunks())

    assert response.status_code == 413
