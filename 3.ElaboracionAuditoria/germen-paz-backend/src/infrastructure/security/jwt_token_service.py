"""Implementación concreta de TokenService usando JWT (python-jose).

La expiración del token es configurable vía `.env`
(`ACCESS_TOKEN_EXPIRE_MINUTES`). Trade-off declarado: este MVP solo
implementa *access tokens*; no incluye *refresh tokens*. Para un
sistema en producción con sesiones largas se recomienda añadir un
refresh token de vida más larga, almacenado de forma segura
(ej. httpOnly cookie) y con posibilidad de revocación server-side.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from src.application.interfaces.token_service import TokenService
from src.domain.exceptions.domain_exceptions import InvalidCredentialsError


class JWTTokenService(TokenService):
    def __init__(self, secret_key: str, algorithm: str, expire_minutes: int) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    def create_access_token(self, subject: str, extra_claims: dict[str, Any] | None = None) -> str:
        now = datetime.now(timezone.utc)
        payload: dict[str, Any] = {
            "sub": subject,
            "iat": now,
            "exp": now + timedelta(minutes=self._expire_minutes),
        }
        if extra_claims:
            payload.update(extra_claims)
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except JWTError as exc:
            raise InvalidCredentialsError("Token inválido o expirado.") from exc
