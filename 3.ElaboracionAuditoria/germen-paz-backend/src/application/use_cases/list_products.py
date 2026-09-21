"""Caso de uso: listar productos con paginación y filtros."""
from __future__ import annotations

from src.application.dtos.product_dto import ProductListOutput, ProductOutput
from src.domain.repositories.product_repository import ProductRepository


class ListProductsUseCase:
    def __init__(self, product_repository: ProductRepository) -> None:
        self._repository = product_repository

    def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        categoria: str | None = None,
        activo: bool | None = None,
        nombre: str | None = None,
    ) -> ProductListOutput:
        items, total = self._repository.list(
            skip=skip, limit=limit, categoria=categoria, activo=activo, nombre=nombre
        )
        outputs = [
            ProductOutput(
                id=p.id,  # type: ignore[arg-type]
                nombre=p.nombre,
                descripcion=p.descripcion,
                precio=p.precio,
                stock=p.stock,
                categoria=p.categoria,
                activo=p.activo,
                creado_por=p.creado_por,
                fecha_creacion=p.fecha_creacion,
                fecha_actualizacion=p.fecha_actualizacion,
            )
            for p in items
        ]
        return ProductListOutput(items=outputs, total=total, skip=skip, limit=limit)
