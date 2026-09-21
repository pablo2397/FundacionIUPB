"""DTOs de autenticación y usuarios."""
from __future__ import annotations

from dataclasses import dataclass

from src.domain.entities.user import UserRole


@dataclass
class RegisterUserInput:
    username: str
    email: str
    password: str
    role: UserRole


@dataclass
class UserOutput:
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool


@dataclass
class LoginInput:
    username: str
    password: str


@dataclass
class TokenOutput:
    access_token: str
    token_type: str = "bearer"
