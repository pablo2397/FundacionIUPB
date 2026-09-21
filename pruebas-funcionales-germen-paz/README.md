# Suite de Pruebas Funcionales — Germen de Paz API

Pruebas funcionales de **caja negra** (usan la librería `requests` contra el
servidor HTTP real, no importan el código de `src/`), organizadas en el
orden lógico de una auditoría QA: **Autenticación → Autorización → CRUD →
Rate limiting**.

Son un complemento a los tests unitarios/de integración que ya vienen dentro
del backend (`germen-paz-backend/tests/`, que usan mocks y `TestClient`).
Esta suite en cambio valida el comportamiento **end-to-end**, tal como lo
vería un cliente real (Postman, el frontend, un atacante).

## Requisitos previos

1. Tener el backend **corriendo** en otra terminal:
   ```bash
   cd germen-paz-backend
   uvicorn src.core.main:app --reload
   ```
2. Python 3.9+ para esta suite (es independiente del backend, no requiere
   el mismo entorno virtual).

**Recomendación:** para no mezclar datos de prueba con tu base de datos de
desarrollo, considera apuntar el backend a un archivo SQLite distinto antes
de correr la suite (en el `.env` del backend: `DATABASE_URL=sqlite:///./germen_paz_test.db`).
Esta suite crea productos y usuarios de prueba que quedan persistidos.

## Instalación

```bash
cd pruebas-funcionales-germen-paz
python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

## Ejecución

### Opción 1: script automatizado (recomendado)

```bash
# Linux/macOS
bash run_functional_tests.sh

# Windows (PowerShell)
.\run_functional_tests.ps1
```

El script verifica primero que el servidor esté disponible (`GET /health`)
y luego corre toda la suite, generando un reporte HTML en
`reporte_pruebas_funcionales.html` (útil como evidencia para el informe de
auditoría).

### Opción 2: pytest directo

```bash
pytest -v
```

### Configuración por variables de entorno

| Variable | Default | Uso |
|---|---|---|
| `FUNCTIONAL_TEST_BASE_URL` | `http://127.0.0.1:8000` | URL del backend a probar |
| `FUNCTIONAL_TEST_ADMIN_USERNAME` | `admin` | Usuario admin sembrado |
| `FUNCTIONAL_TEST_ADMIN_PASSWORD` | `CambiaEstaClave123!` | Contraseña del admin sembrado |
| `FUNCTIONAL_TEST_TIMEOUT` | `10` | Timeout (segundos) de cada petición |

Ejemplo apuntando a otro ambiente:
```bash
FUNCTIONAL_TEST_BASE_URL="http://192.168.1.50:8000" pytest -v
```

## Estructura y orden lógico de las pruebas

```
tests/
├── test_01_autenticacion.py    # PASO 1: login válido/inválido, protección de endpoints
├── test_02_autorizacion.py     # PASO 2: RBAC — admin vs. operador
├── test_03_crud_productos.py   # PASO 3: crear, listar, leer, actualizar, eliminar
└── test_04_rate_limiting.py    # PASO 4: fuerza bruta en /auth/login (ver nota abajo)
```

### Paso 1 — Autenticación (`test_01_autenticacion.py`)
| # | Caso de prueba | Resultado esperado |
|---|---|---|
| 1 | Login con credenciales válidas | `200` + `access_token` |
| 2 | Login con contraseña incorrecta | `401` |
| 3 | Login con usuario inexistente | `401` |
| 4 | Mensaje de error idéntico en ambos casos anteriores | Mismo `detail` (anti-enumeración) |
| 5 | Endpoint protegido sin token | `401` |
| 6 | Endpoint protegido con token inválido/manipulado | `401` |
| 7 | Login con payload incompleto | `422` |

### Paso 2 — Autorización / RBAC (`test_02_autorizacion.py`)
| # | Caso de prueba | Resultado esperado |
|---|---|---|
| 1 | Admin registra un nuevo usuario | `201` |
| 2 | Operador intenta registrar un usuario | `403` |
| 3 | Admin y operador crean productos | `201` para ambos |
| 4 | Admin y operador listan/leen productos | `200` para ambos |
| 5 | Operador intenta eliminar un producto | `403` |
| 6 | Admin elimina un producto | `204` |

### Paso 3 — CRUD de productos (`test_03_crud_productos.py`)
| # | Caso de prueba | Resultado esperado |
|---|---|---|
| 1 | Crear producto válido | `201` |
| 2 | Crear producto con precio negativo | `422` (validación Pydantic) |
| 3 | Crear producto con nombre en blanco | `400` (regla de negocio del dominio) |
| 4 | Crear producto sin campos obligatorios | `422` |
| 5 | Listar con paginación (`skip`/`limit`) | `200`, tamaño de página correcto |
| 6 | Listar filtrando por categoría | `200`, todos los items coinciden |
| 7 | Listar filtrando por nombre parcial | `200`, incluye el producto esperado |
| 8 | Obtener producto existente por ID | `200` |
| 9 | Obtener producto inexistente | `404` |
| 10 | Actualizar completo (PUT) | `200`, campos reflejan el cambio |
| 11 | Actualizar parcial (PATCH) — solo un campo | `200`, resto de campos intactos |
| 12 | Actualizar con stock negativo | `422` |
| 13 | Actualizar producto inexistente | `404` |
| 14 | Eliminar producto (soft delete) | `204`, luego `GET` muestra `activo=false` |
| 15 | Eliminar producto inexistente | `404` |

### Paso 4 — Rate limiting (`test_04_rate_limiting.py`)
Agota intencionalmente el límite de 5 intentos/minuto en `/auth/login` y
verifica que el servidor responde `429`. **Se ejecuta al final a propósito**:
si corriera antes, dejaría el límite consumido y haría fallar (por `429`, no
por un error real) los logins que los pasos 2 y 3 necesitan para preparar
sus datos.

> Si vuelves a correr la suite completa justo después de este paso, espera
> ~60 segundos para que la ventana del rate limit se libere.

## Notas de diseño

- Los usuarios de prueba (`operador`) se crean con un sufijo aleatorio
  (`uuid4`) en cada ejecución, para poder reejecutar la suite varias veces
  sin chocar con el `409 Conflict` de "usuario ya existe".
- `admin_token` y `operador_token` tienen alcance de **sesión** de pytest
  (se calculan una sola vez): reduce las llamadas a `/auth/login` durante la
  suite normal, dejando margen dentro del rate limit para el paso 4.
- Si el paso 1 ya consumió la cuota de 5 intentos/minuto (por ejemplo, al
  reejecutar la suite dos veces seguidas), los fixtures de login del paso 2
  detectan el `429` y **esperan ~65 segundos y reintentan automáticamente**
  en lugar de fallar. Esto puede hacer que una corrida ocasional tarde un
  poco más; es el comportamiento correcto para un cliente que respeta un
  rate limit real, no un error de la suite.
- Estas pruebas asumen el usuario admin y sus credenciales por defecto del
  `.env` de ejemplo del backend. Si los cambiaste, ajusta las variables de
  entorno `FUNCTIONAL_TEST_ADMIN_USERNAME` / `FUNCTIONAL_TEST_ADMIN_PASSWORD`.
