"""Schemas Pydantic (request/response) para autenticación y usuarios."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.domain.entities.user import UserRole


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, examples=["operador1"])
    email: str = Field(..., min_length=5, max_length=120, examples=["operador1@germendepaz.org"])
    password: str = Field(..., min_length=8, max_length=128, examples=["ClaveSegura123!"])
    role: UserRole = Field(..., examples=[UserRole.OPERADOR])


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    username: str = Field(..., examples=["admin"])
    password: str = Field(..., examples=["CambiaEstaClave123!"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ErrorResponse(BaseModel):
    """Schema estándar de error, usado en las respuestas documentadas en Swagger."""

    detail: str
