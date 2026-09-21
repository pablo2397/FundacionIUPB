#!/usr/bin/env bash
# Ejecuta la suite completa de pruebas funcionales y genera un reporte HTML.
set -euo pipefail
cd "$(dirname "$0")"

BASE_URL="${FUNCTIONAL_TEST_BASE_URL:-http://127.0.0.1:8000}"

echo "Verificando que el servidor esté disponible en ${BASE_URL}..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/health" || true)
if [ "${HTTP_CODE}" != "200" ]; then
  echo "ERROR: el servidor no respondió correctamente en ${BASE_URL}/health (código: ${HTTP_CODE})."
  echo "Arráncalo primero con: uvicorn src.core.main:app --reload"
  exit 1
fi

echo "Servidor disponible. Ejecutando pruebas funcionales en orden (autenticación -> autorización -> CRUD -> rate limiting)..."
pytest -v --html=reporte_pruebas_funcionales.html --self-contained-html

echo "Reporte generado en ./reporte_pruebas_funcionales.html"
