from fastapi import FastAPI
from pydantic import BaseModel

from app.config import get_settings


class HealthResponse(BaseModel):
    status: str
    service: str


settings = get_settings()
app = FastAPI(title=settings.app_name)


@app.get("/health", response_model=HealthResponse, tags=["operación"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.app_name)

