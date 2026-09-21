"""Caso de uso: eliminar (soft delete) un producto.

Decisión de diseño: se usa *soft delete* (marcar `activo=False`) en
lugar de borrado físico, para conservar trazabilidad e integridad
referencial (ej. reportes históricos, auditoría). El trade-off es que
las consultas deben filtrar explícitamente por `activo` y la tabla
crece indefinidamente; para un MVP esto es aceptable y se documenta
en el README.
"""
from __future__ import annotations

from src.domain.exceptions.domain_exceptions import ProductNotFoundError
from src.domain.repositories.product_repository import ProductRepository


class DeleteProductUseCase:
    def __init__(self, product_repository: ProductRepository) -> None:
        self._repository = product_repository

    def execute(self, product_id: int) -> None:
        product = self._repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(f"Producto con id {product_id} no encontrado.")
        self._repository.soft_delete(product_id)
