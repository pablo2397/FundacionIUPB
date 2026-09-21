# Ejecuta la suite completa de pruebas funcionales y genera un reporte HTML.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$BaseUrl = if ($env:FUNCTIONAL_TEST_BASE_URL) { $env:FUNCTIONAL_TEST_BASE_URL } else { "http://127.0.0.1:8000" }

Write-Host "Verificando que el servidor esté disponible en $BaseUrl..."
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -ne 200) {
        throw "El servidor respondió con código $($response.StatusCode)"
    }
} catch {
    Write-Host "ERROR: el servidor no responde en $BaseUrl/health."
    Write-Host "Arráncalo primero con: uvicorn src.core.main:app --reload"
    exit 1
}

Write-Host "Servidor disponible. Ejecutando pruebas funcionales en orden (autenticación -> autorización -> CRUD -> rate limiting)..."
pytest -v --html=reporte_pruebas_funcionales.html --self-contained-html

Write-Host "Reporte generado en .\reporte_pruebas_funcionales.html"
