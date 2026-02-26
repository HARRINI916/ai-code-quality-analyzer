$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"
$frontendDir = Join-Path $repoRoot "frontend"

if (-not (Test-Path $backendDir)) {
  throw "Backend directory not found: $backendDir"
}

if (-not (Test-Path $frontendDir)) {
  throw "Frontend directory not found: $frontendDir"
}

$pythonExe = if (Test-Path (Join-Path $repoRoot ".venv\\Scripts\\python.exe")) {
  Join-Path $repoRoot ".venv\\Scripts\\python.exe"
} elseif (Test-Path (Join-Path $backendDir ".venv\\Scripts\\python.exe")) {
  Join-Path $backendDir ".venv\\Scripts\\python.exe"
} else {
  "python"
}

Write-Host "Starting backend on http://localhost:8000 ..."
Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$backendDir'; & '$pythonExe' -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
)

Write-Host "Starting frontend on http://localhost:5173 ..."
Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$frontendDir'; npm run dev"
)

Write-Host "Both processes launched."
