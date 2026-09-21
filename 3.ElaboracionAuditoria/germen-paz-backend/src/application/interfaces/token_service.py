"""Puerto hacia infraestructura: emisión y validación de tokens JWT."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class TokenService(ABC):
    @abstractmethod
    def create_access_token(self, subject: str, extra_claims: dict[str, Any] | None = None) -> str:
        ...

    @abstractmethod
    def decode_token(self, token: str) -> dict[str, Any]:
        """Debe lanzar una excepción si el token es inválido o expiró."""
        ...
