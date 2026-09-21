"""Configuración centralizada de la aplicación.

Todas las variables sensibles se cargan desde un archivo `.env`
(nunca se hardcodean en el código). Ver `.env.example` para la lista
completa de variables requeridas.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Aplicación
    APP_NAME: str = "Germen de Paz - API de Productos"
    ENVIRONMENT: str = "development"  # development | production
    DEBUG: bool = True

    # Base de datos
    DATABASE_URL: str = "sqlite:///./germen_paz.db"

    # Seguridad / JWT
    SECRET_KEY: str  # Obligatorio, sin valor por defecto: debe venir del .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Seed del admin inicial
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@germendepaz.org"
    ADMIN_PASSWORD: str  # Obligatorio, sin valor por defecto: debe venir del .env

    # CORS (lista separada por comas en el .env, ej: "http://localhost:3000,https://germendepaz.org")
    CORS_ORIGINS: str = "http://localhost:3000"

    # Rate limiting
    LOGIN_RATE_LIMIT: str = "5/minute"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Cachea la instancia de Settings (se lee el .env una sola vez)."""
    return Settings()  # type: ignore[call-arg]
