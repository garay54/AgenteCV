"""Validación de los encabezados enviados al endpoint del agente."""

from __future__ import annotations

from hmac import compare_digest
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings, get_settings


# auto_error=False permite devolver el mismo error seguro cuando falta el
# encabezado, el esquema no es Bearer o la credencial está mal formada.
bearer_scheme = HTTPBearer(auto_error=False)


def require_agent_access(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    """Exige JSON y valida la clave Bearer configurada para el agente.

    La función no registra ni devuelve la credencial recibida. ``compare_digest``
    evita comparar secretos con una operación de igualdad convencional.
    """

    media_type = (
        request.headers.get("content-type", "")
        .split(";", maxsplit=1)[0]
        .strip()
        .lower()
    )
    if media_type != "application/json":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Content-Type debe ser application/json.",
        )

    if settings.agent_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio no está configurado correctamente.",
        )

    expected_key = settings.agent_api_key.get_secret_value()
    credentials_are_valid = (
        credentials is not None
        and credentials.scheme.lower() == "bearer"
        and compare_digest(credentials.credentials, expected_key)
    )

    if not credentials_are_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
            headers={"WWW-Authenticate": "Bearer"},
        )
