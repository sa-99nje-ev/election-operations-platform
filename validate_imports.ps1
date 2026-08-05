# ============================================================
# validate_imports.ps1 - Python Import Validation
# ============================================================
# Checks: All Python files can import their dependencies
# ============================================================

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "PHASE B: Import Validation" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Project Root: $PWD" -ForegroundColor Yellow
Write-Host ""

# ============================================================
# 1. Validate Core Imports
# ============================================================

Write-Host "[1] Validating core imports..." -ForegroundColor Yellow
Write-Host "-" * 60 -ForegroundColor Gray

$coreModules = @(
    "flask",
    "flask_jwt_extended",
    "flask_sqlalchemy",
    "sqlalchemy",
    "sqlalchemy.orm",
    "celery",
    "celery.result",
    "celery.signals",
    "redis",
    "marshmallow",
    "werkzeug",
    "psycopg",        # Updated from psycopg2 to match psycopg v3
    "bcrypt",
    "dotenv",         # Updated from python_dotenv to match python import name
    "plotly",
    "locust",
    "pytest"
)

$failedModules = @()

foreach ($mod in $coreModules) {
    $testCmd = "python -c 'import $mod' 2>&1"
    $result = Invoke-Expression $testCmd
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ $mod" -ForegroundColor Green
    } else {
        $failedModules += "$mod : $result"
        Write-Host "  ❌ $mod" -ForegroundColor Red
    }
}

if ($failedModules.Count -eq 0) {
    Write-Host ""
    Write-Host "  ✅ All core imports resolved" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "  ❌ $($failedModules.Count) module(s) failed to import:" -ForegroundColor Red
    $failedModules | ForEach-Object { Write-Host "     - $_" -ForegroundColor Red }
}

Write-Host ""

# ============================================================
# 2. Validate Application Imports
# ============================================================

Write-Host "[2] Validating application imports..." -ForegroundColor Yellow
Write-Host "-" * 60 -ForegroundColor Gray

$appModules = @(
    "app",
    "app.api",
    "app.api.auth",
    "app.api.voters",
    "app.api.candidates",
    "app.api.constituencies",
    "app.api.polling_booths",
    "app.api.voting",
    "app.api.results",
    "app.api.health",
    "app.api.users",
    "app.models",
    "app.models.user",
    "app.models.voter",
    "app.models.candidate",
    "app.models.constituency",
    "app.models.polling_booth",
    "app.models.voting_record",
    "app.models.audit_log",
    "app.models.refresh_token",
    "app.repositories",
    "app.repositories.base",
    "app.repositories.user_repository",
    "app.repositories.voter_repository",
    "app.repositories.candidate_repository",
    "app.repositories.constituency_repository",
    "app.repositories.polling_booth_repository",
    "app.repositories.voting_record_repository",
    "app.repositories.audit_log_repository",
    "app.repositories.refresh_token_repository",
    "app.services",
    "app.services.auth_service",
    "app.services.user_service",
    "app.services.voter_service",
    "app.services.candidate_service",
    "app.services.constituency_service",
    "app.services.polling_booth_service",
    "app.services.voting_service",
    "app.services.results_service",
    "app.services.vote_processing_service",
    "app.services.metrics_service",
    "app.services.request_factory",
    "app.schemas",
    "app.schemas.auth_schema",
    "app.schemas.user_schema",
    "app.schemas.voter_schema",
    "app.schemas.candidate_schema",
    "app.schemas.constituency_schema",
    "app.schemas.polling_booth_schema",
    "app.schemas.voting_schema",
    "app.utils",
    "app.utils.enums",
    "app.utils.exceptions",
    "app.utils.password",
    "app.utils.tokens",
    "app.utils.rbac",
    "app.utils.security",
    "app.utils.error_handlers",
    "app.utils.logging_config",
    "app.queue",
    "app.queue.queue_service",
    "app.queue.redis_client",
    "app.tasks",
    "app.tasks.vote_tasks",
    "app.config",
    "app.config.settings",
    "app.config.development",
    "app.config.testing",
    "app.config.production",
    "app.celery_app",
    "app.extensions",
    "app.auth",
    "app.auth.routes",
    "app.auth.schemas",
    "dashboard",
    "tasks",
    "tasks.vote_tasks"
)

$failedAppModules = @()

foreach ($mod in $appModules) {
    $testCmd = "python -c 'import $mod' 2>&1"
    $result = Invoke-Expression $testCmd
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ $mod" -ForegroundColor Green
    } else {
        $failedAppModules += "$mod : $result"
        Write-Host "  ❌ $mod" -ForegroundColor Red
    }
}

if ($failedAppModules.Count -eq 0) {
    Write-Host ""
    Write-Host "  ✅ All application imports resolved" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "  ❌ $($failedAppModules.Count) module(s) failed to import:" -ForegroundColor Red
    $failedAppModules | ForEach-Object { Write-Host "     - $_" -ForegroundColor Red }
}

Write-Host ""

# ============================================================
# Summary
# ============================================================

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$totalErrors = $failedModules.Count + $failedAppModules.Count

if ($totalErrors -eq 0) {
    Write-Host "✅ STATUS: ALL IMPORTS VALID" -ForegroundColor Green
} else {
    Write-Host "❌ STATUS: $totalErrors IMPORT ERROR(S) FOUND" -ForegroundColor Red
}

Write-Host ""