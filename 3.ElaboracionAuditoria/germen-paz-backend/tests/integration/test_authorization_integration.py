"""Prueba de integración: verifica que la autorización por rol (RBAC)
funciona de extremo a extremo sobre la API real, usando una base de
datos SQLite en memoria (no se usa la base de datos de desarrollo).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.main import app
from src.infrastructure.database.connection import Base, get_db

# Motor SQLite en memoria, compartido entre requests gracias a StaticPool.
_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def _override_get_db():
    db = _TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module", autouse=True)
def _setup_database():
    Base.metadata.create_all(bind=_engine)
    app.dependency_overrides[get_db] = _override_get_db
    # Crea el admin inicial directamente contra la DB de test.
    from src.infrastructure.config.settings import get_settings
    from src.infrastructure.database.seed import seed_admin_user

    db = _TestingSessionLocal()
    try:
        seed_admin_user(db, get_settings())
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=_engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _login(client: TestClient, username: str, password: str) -> str:
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


class TestAuthorizationRBAC:
    def test_operador_no_puede_registrar_usuarios(self, client: TestClient):
        admin_token = _login(client, "admin", "CambiaEstaClave123!")

        # Crea un operador usando al admin.
        create_resp = client.post(
            "/auth/register",
            json={
                "username": "operador_rbac",
                "email": "operador_rbac@germendepaz.org",
                "password": "OperadorPass123!",
                "role": "operador",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert create_resp.status_code == 201, create_resp.text

        operador_token = _login(client, "operador_rbac", "OperadorPass123!")

        # El operador intenta registrar a otro usuario: debe ser rechazado (403).
        forbidden_resp = client.post(
            "/auth/register",
            json={
                "username": "otro",
                "email": "otro@germendepaz.org",
                "password": "Clave123456!",
                "role": "operador",
            },
            headers={"Authorization": f"Bearer {operador_token}"},
        )
        assert forbidden_resp.status_code == 403

    def test_operador_no_puede_eliminar_producto(self, client: TestClient):
        admin_token = _login(client, "admin", "CambiaEstaClave123!")

        create_resp = client.post(
            "/products",
            json={"nombre": "Libreta", "descripcion": "", "precio": 5000, "stock": 10, "categoria": "papeleria"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert create_resp.status_code == 201, create_resp.text
        product_id = create_resp.json()["id"]

        operador_token = _login(client, "operador_rbac", "OperadorPass123!")

        delete_resp = client.delete(
            f"/products/{product_id}", headers={"Authorization": f"Bearer {operador_token}"}
        )
        assert delete_resp.status_code == 403

    def test_sin_token_devuelve_401(self, client: TestClient):
        response = client.get("/products")
        assert response.status_code == 401
