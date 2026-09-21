"""DTOs (Data Transfer Objects) de entrada/salida de los casos de uso de productos.

Estos DTOs son independientes de Pydantic/FastAPI: son simples
dataclasses usadas como contrato entre la capa de aplicación y quien
la invoque (en este caso, la capa `core`).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class CreateProductInput:
    nombre: str
    descripcion: str
    precio: float
    stock: int
    categoria: str
    creado_por: int


@dataclass
class UpdateProductInput:
    nombre: str | None = None
    descripcion: str | None = None
    precio: float | None = None
    stock: int | None = None
    categoria: str | None = None
    activo: bool | None = None


@dataclass
class ProductOutput:
    id: int
    nombre: str
    descripcion: str
    precio: float
    stock: int
    categoria: str
    activo: bool
    creado_por: int
    fecha_creacion: datetime | None
    fecha_actualizacion: datetime | None


@dataclass
class ProductListOutput:
    items: list[ProductOutput]
    total: int
    skip: int
    limit: int
