# Germen de Paz — API de Gestión de Productos (MVP Backend)

MVP de backend en **Python 3.11+ / FastAPI**, construido con **Clean
Architecture** y **seguridad por diseño**, pensado como caso de
estudio para una evaluación de seguridad posterior (pruebas de
penetración, checklist OWASP API Security Top 10, etc.) sobre el
sistema transaccional de gestión de productos de la Fundación
Germen de Paz.

## Decisiones de arquitectura y seguridad

El proyecto sigue **Clean Architecture** con 4 capas e inversión de
dependencias: `domain` (entidades y reglas de negocio puras, sin
imports de FastAPI/SQLAlchemy), `application` (casos de uso que
orquestan el dominio a través de interfaces abstractas —puertos—
hacia infraestructura), `infrastructure` (implementaciones concretas:
SQLAlchemy, JWT, bcrypt, slowapi) y `core` (capa HTTP: routers,
schemas Pydantic, dependencias de FastAPI). Las capas internas
(`domain`, `application`) no conocen a las externas; `core` es el
único punto donde se "ensamblan" las implementaciones concretas
(ver `core/dependencies/providers.py`), lo que facilita sustituir
SQLite por otro motor, o JWT por otro esquema, sin tocar la lógica
de negocio ni los casos de uso.

En seguridad se optó por: JWT de solo *access token* (sin refresh
token, ver trade-off abajo), contraseñas con bcrypt vía `passlib`,
RBAC explícito por endpoint con `Depends(require_role(...))`,
validación estricta de entradas con Pydantic, queries 100% vía ORM
(sin concatenación de SQL), *soft delete* en productos (se conserva
trazabilidad e integridad referencial en vez de borrado físico),
rate limiting en `/auth/login` con `slowapi`, manejo centralizado de
errores que nunca expone stack traces en producción, y variables
sensibles cargadas exclusivamente desde `.env` vía
`pydantic-settings`.

El diseño es **síncrono** (SQLAlchemy síncrono, no `asyncio`):
SQLite serializa escrituras a nivel de archivo de todas formas, por
lo que `aiosqlite` no aporta concurrencia real en este contexto, y el
driver síncrono es más simple de testear con mocks/`TestClient` y
más maduro en el ecosistema (Alembic, etc.). Si el proyecto migra a
Postgres con alta concurrencia, se recomienda pasar a SQLAlchemy
async.

**Trade-offs declarados:**
- *Soft delete vs. hard delete*: se eligió soft delete (`activo=False`) para conservar auditoría/histórico; el costo es que la tabla crece indefinidamente y las consultas deben filtrar por `activo` explícitamente.
- *JWT sin refresh token*: el MVP solo emite access tokens con expiración corta (`ACCESS_TOKEN_EXPIRE_MINUTES`); no hay revocación server-side ni refresh token. Para producción se recomienda añadir refresh tokens con almacenamiento seguro (httpOnly cookie) y posibilidad de revocación.

## Estructura del proyecto

```
germen-paz-backend/
├── src/
│   ├── domain/            # Entidades, excepciones y contratos de repositorio
│   ├── application/       # Casos de uso, DTOs, interfaces hacia infraestructura
│   ├── infrastructure/    # SQLAlchemy, JWT, bcrypt, rate limiter, settings, seed
│   └── core/               # FastAPI: routers, schemas, dependencias, middlewares, main.py
├── tests/
│   ├── unit/               # Casos de uso con repositorios fake (sin SQLite real)
│   ├── integration/        # RBAC de extremo a extremo con TestClient + SQLite en memoria
│   └── conftest.py
├── scripts/run_tests.sh
├── requirements.txt
├── .env.example
└── .env                    # Ya incluido y listo para ejecutar en local/desarrollo
```

## Instalación y ejecución

Requisitos: Python 3.11 o superior.

```bash
# 1. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. (Opcional) Revisar/editar variables de entorno
#    El proyecto ya incluye un archivo .env funcional para desarrollo local.
#    Para producción, copia .env.example como .env y cambia SECRET_KEY,
#    ADMIN_PASSWORD y CORS_ORIGINS.
cp .env.example .env   # opcional, solo si quieres regenerar tus propios valores

# 4. Ejecutar el servidor
uvicorn src.core.main:app --reload
```

La API quedará disponible en `http://127.0.0.1:8000`.

- Swagger UI: `http://127.0.0.1:8000/docs`
- Redoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`

Al arrancar, la aplicación crea automáticamente las tablas en SQLite
y siembra el usuario **admin** inicial con las credenciales definidas
en `.env` (por defecto: usuario `admin`, contraseña
`CambiaEstaClave123!` — **cámbiala antes de cualquier uso real**).

### Probar rápidamente con curl

```bash
# Login como admin
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "CambiaEstaClave123!"}'

# Usar el token devuelto para crear un producto
curl -X POST http://127.0.0.1:8000/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"nombre": "Cuaderno", "descripcion": "Ecológico", "precio": 12500, "stock": 50, "categoria": "papeleria"}'
```

## Ejecutar las pruebas

```bash
bash scripts/run_tests.sh
```

Esto ejecuta `pytest` con reporte de cobertura (`pytest-cov`) y
**falla si la cobertura total baja del 70%**. El reporte HTML queda
en `htmlcov/index.html`. También puedes ejecutar `pytest` directamente:

```bash
pytest --cov=src --cov-report=term-missing tests/
```

Las pruebas unitarias (`tests/unit/`) usan repositorios *fake* en
memoria (no tocan SQLite real), y cubren: casos de uso de productos
(crear, listar, obtener, actualizar, eliminar), autenticación (login
exitoso/fallido, usuario inactivo) y registro de usuarios. La prueba
de integración (`tests/integration/`) valida RBAC de extremo a
extremo contra la API real usando SQLite en memoria.

## Controles de seguridad: implementados vs. pendientes (insumo OWASP API Security Top 10)

| Control | Estado | Detalle |
|---|---|---|
| Autenticación (JWT) | ✅ Implementado | Access token JWT firmado (HS256), expiración configurable |
| Hashing de contraseñas | ✅ Implementado | bcrypt vía `passlib`, nunca texto plano |
| Autorización RBAC | ✅ Implementado | `require_role()` explícito por endpoint (admin / operador) |
| Validación de entradas | ✅ Implementado | Pydantic con tipos, longitudes y rangos en cada schema |
| Inyección SQL | ✅ Mitigado | 100% ORM (SQLAlchemy), sin concatenación de queries |
| Rate limiting en login | ✅ Implementado (básico) | `slowapi`, 5 intentos/minuto por IP (configurable) |
| Manejo centralizado de errores | ✅ Implementado | No expone stack traces en `ENVIRONMENT=production` |
| Cabeceras de seguridad | ✅ Implementado (mínimo) | `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, HSTS en producción |
| CORS restringido | ✅ Implementado | Orígenes explícitos vía `CORS_ORIGINS` en `.env` |
| Secretos vía variables de entorno | ✅ Implementado | `pydantic-settings` + `.env`, sin hardcodeo |
| Logging de eventos de auth | ✅ Implementado | Login exitoso/fallido registrado, sin loguear contraseñas/tokens |
| Soft delete con auditoría | ✅ Implementado | `activo=False`, sin borrado físico |
| **BOLA (Broken Object Level Authorization)** | ⚠️ Parcial | RBAC por rol implementado; falta ownership check por recurso individual (ej. "solo el creador puede editar") si el negocio lo requiere |
| Refresh tokens / revocación de sesión | ❌ Fuera de alcance del MVP | Solo access token; revocación server-side no implementada |
| Rotación de `SECRET_KEY` / gestión de secretos en vault | ❌ Fuera de alcance del MVP | `.env` es suficiente para MVP; producción debería usar un secret manager |
| Auditoría persistente (tabla de logs en DB) | ❌ Fuera de alcance del MVP | Actualmente solo logging a stdout, no a tabla auditable |
| Protección contra mass assignment avanzada | ⚠️ Parcial | Pydantic ya evita campos no declarados, pero no hay allow-list explícita por rol |
| HTTPS / TLS | ❌ Fuera de alcance del MVP | Debe terminarse en un proxy (nginx, load balancer) en producción |
| Protección anti-CSRF | N/A | No aplica: API stateless con Bearer token, no usa cookies de sesión |
| Content Security Policy (CSP) | ❌ No implementado | Aplicaría si se sirve HTML/frontend desde el mismo dominio |
| Dependency scanning / SCA automatizado | ❌ Fuera de alcance del MVP | Recomendado incorporar `pip-audit` o similar en CI |

Esta tabla está pensada como punto de partida para el checklist de
evaluación de controles (OWASP API Security Top 10) que se realizará
en la siguiente fase del proyecto.
