"""Entidad de dominio: Producto."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.domain.exceptions.domain_exceptions import InvalidProductDataError


@dataclass
class Product:
    """Entidad de producto del dominio.

    Contiene únicamente reglas de negocio puras; la persistencia y la
    validación de formato de entrada (tipos, longitudes máximas de
    request HTTP) viven en otras capas.
    """

    id: int | None
    nombre: str
    descripcion: str
    precio: float
    stock: int
    categoria: str
    activo: bool
    creado_por: int
    fecha_creacion: datetime | None = None
    fecha_actualizacion: datetime | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Reglas de negocio invariantes del producto."""
        if not self.nombre or not self.nombre.strip():
            raise InvalidProductDataError("El nombre del producto no puede estar vacío.")
        if self.precio < 0:
            raise InvalidProductDataError("El precio no puede ser negativo.")
        if self.stock < 0:
            raise InvalidProductDataError("El stock no puede ser negativo.")

    def desactivar(self) -> None:
        """Soft delete a nivel de dominio: el producto se marca inactivo."""
        self.activo = False

    def actualizar_stock(self, nuevo_stock: int) -> None:
        if nuevo_stock < 0:
            raise InvalidProductDataError("El stock no puede ser negativo.")
        self.stock = nuevo_stock
