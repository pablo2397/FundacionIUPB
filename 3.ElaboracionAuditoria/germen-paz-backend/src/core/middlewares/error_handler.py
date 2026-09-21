"""Manejo centralizado de errores.

En producción (`ENVIRONMENT=production`) las excepciones no
controladas nunca exponen stack traces ni rutas internas del
sistema al cliente: se registran en el log del servidor y se
devuelve un mensaje genérico. En desarrollo se puede ver más
detalle para facilitar la depuración.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.domain.exceptions.domain_exceptions import DomainError
from src.infrastructure.config.settings import get_settings

logger = logging.getLogger("germen_paz.errors")


def register_exception_handlers(app: FastAPI) -> None:
    settings = get_settings()

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        # Fallback por si algún DomainError no fue capturado explícitamente
        # en el router correspondiente.
        logger.warning("DomainError no manejado explícitamente: %s", exc)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Error no controlado en %s: %s", request.url.path, exc, exc_info=True)
        detail = str(exc) if not settings.is_production else "Ha ocurrido un error interno."
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": detail},
        )
