"""Schemas Pydantic (request/response) para el recurso Producto.

Estos schemas son responsables de la validación estricta de entradas
HTTP (tipos, longitudes, rangos), separada de las reglas de negocio
del dominio.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductCreateRequest(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150, examples=["Cuaderno ecológico A5"])
    descripcion: str = Field("", max_length=1000, examples=["Cuaderno reciclado, 100 hojas"])
    precio: float = Field(..., ge=0, examples=[12500.0])
    stock: int = Field(..., ge=0, examples=[50])
    categoria: str = Field(..., min_length=1, max_length=100, examples=["papeleria"])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Cuaderno ecológico A5",
                "descripcion": "Cuaderno reciclado, 100 hojas",
                "precio": 12500.0,
                "stock": 50,
                "categoria": "papeleria",
            }
        }
    )


class ProductUpdateRequest(BaseModel):
    """Actualización completa (PUT): todos los campos son requeridos por el caso de uso,
    pero se permiten opcionales a nivel de schema para reusar en PATCH también."""

    nombre: str | None = Field(None, min_length=1, max_length=150)
    descripcion: str | None = Field(None, max_length=1000)
    precio: float | None = Field(None, ge=0)
    stock: int | None = Field(None, ge=0)
    categoria: str | None = Field(None, min_length=1, max_length=100)
    activo: bool | None = None


class ProductPatchRequest(ProductUpdateRequest):
    """Actualización parcial (PATCH): todos los campos opcionales."""


class ProductResponse(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    skip: int
    limit: int
