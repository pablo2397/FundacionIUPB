#!/usr/bin/env bash
# Ejecuta toda la suite de pruebas con reporte de cobertura.
# Falla (exit code != 0) si la cobertura total es menor al umbral definido.
set -euo pipefail

cd "$(dirname "$0")/.."

COVERAGE_THRESHOLD=70

echo "Ejecutando pruebas con pytest + cobertura (umbral mínimo: ${COVERAGE_THRESHOLD}%)..."

pytest \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=html:htmlcov \
  --cov-fail-under="${COVERAGE_THRESHOLD}" \
  tests/

echo "Reporte HTML de cobertura generado en ./htmlcov/index.html"
