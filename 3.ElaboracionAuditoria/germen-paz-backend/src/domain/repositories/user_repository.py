"""Contrato (puerto) abstracto del repositorio de usuarios."""
from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User:
        ...

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        ...

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        ...

    @abstractmethod
    def list(self, skip: int = 0, limit: int = 20) -> tuple[list[User], int]:
        ...
