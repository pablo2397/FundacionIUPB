"""Implementación concreta de PasswordHasher usando bcrypt (passlib).

Las contraseñas nunca se almacenan ni se registran en logs en texto
plano; únicamente se persiste el hash.
"""
from __future__ import annotations

from passlib.context import CryptContext

from src.application.interfaces.password_hasher import PasswordHasher

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BcryptPasswordHasher(PasswordHasher):
    def hash(self, plain_password: str) -> str:
        return _pwd_context.hash(plain_password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return _pwd_context.verify(plain_password, hashed_password)
