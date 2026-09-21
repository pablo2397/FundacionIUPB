"""Contrato (puerto) abstracto del repositorio de productos.

La capa de dominio y de aplicación dependen únicamente de esta
interfaz, nunca de una implementación concreta (SQLAlchemy, etc.).
Esto es Inversión de Dependencias: el detalle (infrastructure)
depende de la abstracción (domain), no al revés.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.product import Product


class ProductRepository(ABC):
    @abstractmethod
    def create(self, product: Product) -> Product:
        ...

    @abstractmethod
    def get_by_id(self, product_id: int) -> Product | None:
        ...

    @abstractmethod
    def list(
        self,
        skip: int = 0,
        limit: int = 20,
        categoria: str | None = None,
        activo: bool | None = None,
        nombre: str | None = None,
    ) -> tuple[list[Product], int]:
        """Devuelve (items, total) para soportar paginación."""
        ...

    @abstractmethod
    def update(self, product: Product) -> Product:
        ...

    @abstractmethod
    def soft_delete(self, product_id: int) -> None:
        ...
