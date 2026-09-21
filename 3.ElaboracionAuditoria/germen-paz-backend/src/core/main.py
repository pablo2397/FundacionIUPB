"""Punto de entrada de la aplicación.

Ensambla: instancia de FastAPI, CORS restringido, cabeceras de
seguridad, rate limiting, manejo centralizado de errores, routers y
el seed del usuario admin inicial.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.core.middlewares.error_handler import register_exception_handlers
from src.core.middlewares.logging_config import setup_logging
from src.core.routers.auth_router import router as auth_router
from src.core.routers.product_router import router as product_router
from src.infrastructure.config.settings import get_settings
from src.infrastructure.database.connection import Base, SessionLocal, engine
from src.infrastructure.database.seed import seed_admin_user
from src.infrastructure.security.rate_limiter import limiter

settings = get_settings()
setup_logging(debug=settings.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: crea las tablas (si no existen) y siembra el admin inicial.
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_admin_user(db, settings)
    finally:
        db.close()
    yield
    # Shutdown: no se requiere limpieza adicional para SQLite.


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "API REST para la gestión de productos de la Fundación Germen de Paz. "
        "MVP construido con Clean Architecture y seguridad por diseño "
        "(OWASP API Security Top 10) como caso de estudio para una evaluación "
        "de seguridad posterior."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# --- Rate limiting (slowapi) ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS restringido a orígenes explícitos definidos en .env ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# --- Cabeceras de seguridad recomendadas ---
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # HSTS solo tiene sentido detrás de HTTPS real (ej. producción tras un proxy TLS).
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return response


# --- Manejo centralizado de errores ---
register_exception_handlers(app)

# --- Routers ---
app.include_router(auth_router)
app.include_router(product_router)


@app.get("/health", tags=["Salud"], summary="Health check")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
