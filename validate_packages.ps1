# ============================================================
# validate_packages.ps1 - Python Package Structure Validation
# ============================================================
# Checks:
# 1. __init__.py in Python packages (app/, tests/, dashboard/, tasks/)
# 2. Package discovery via import statements
# 3. Orphaned __pycache__ directories
# ============================================================

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "PHASE B: Package Structure Validation" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Project Root: $PWD" -ForegroundColor Yellow
Write-Host ""

# ============================================================
# 1. Check __init__.py in Python Packages Only
# ============================================================

Write-Host "[1] Checking __init__.py files..." -ForegroundColor Yellow
Write-Host "-" * 60 -ForegroundColor Gray

$packageRoots = @("app", "tests", "dashboard", "tasks")

$missingInit = @()

foreach ($root in $packageRoots) {
    if (-not (Test-Path $root)) { continue }
    
    $dirs = Get-ChildItem -Path $root -Recurse -Directory | Where-Object {
        $_.Name -notmatch "^__pycache__$" -and
        $_.Name -notmatch "^\.pytest_cache$" -and
        $_.Name -notmatch "^\.mypy_cache$" -and
        $_.Name -notmatch "^\.ruff_cache$" -and
        $_.FullName -notmatch "\\\\.venv\\\\" -and
        $_.FullName -notmatch "\\\\venv\\\\"
    }
    
    foreach ($dir in $dirs) {
        $initPath = Join-Path $dir.FullName "__init__.py"
        if (-not (Test-Path $initPath)) {
            $relPath = $dir.FullName.Substring((Get-Location).Path.Length + 1)
            $missingInit += $relPath
            Write-Host "  ❌ MISSING: $relPath\__init__.py" -ForegroundColor Red
        }
    }
}

if ($missingInit.Count -eq 0) {
    Write-Host "  ✅ All Python packages have __init__.py" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "  ❌ $($missingInit.Count) package(s) missing __init__.py:" -ForegroundColor Red
    $missingInit | ForEach-Object { Write-Host "     - $_" -ForegroundColor Red }
}

Write-Host ""

# ============================================================
# 2. Package Discovery
# ============================================================

Write-Host "[2] Testing package discovery..." -ForegroundColor Yellow
Write-Host "-" * 60 -ForegroundColor Gray

$packages = @(
    "app",
    "app.api",
    "app.models",
    "app.repositories",
    "app.services",
    "app.schemas",
    "app.utils",
    "app.queue",
    "app.tasks",
    "app.config",
    "tests",
    "tests.unit",
    "tests.integration",
    "dashboard",
    "tasks"
)

$failedPackages = @()

foreach ($pkg in $packages) {
    $testCmd = "python -c 'import $pkg' 2>&1"
    $result = Invoke-Expression $testCmd
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ $pkg" -ForegroundColor Green
    } else {
        $failedPackages += "$pkg : $result"
        Write-Host "  ❌ $pkg" -ForegroundColor Red
    }
}

if ($failedPackages.Count -eq 0) {
    Write-Host ""
    Write-Host "  ✅ All packages discovered successfully" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "  ❌ $($failedPackages.Count) package(s) failed to import:" -ForegroundColor Red
    $failedPackages | ForEach-Object { Write-Host "     - $_" -ForegroundColor Red }
}

Write-Host ""

# ============================================================
# 3. Orphaned __pycache__ Directories
# ============================================================

Write-Host "[3] Checking for orphaned __pycache__ directories..." -ForegroundColor Yellow
Write-Host "-" * 60 -ForegroundColor Gray

$pycacheDirs = Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Where-Object {
    $_.FullName -notmatch "\\\\.venv\\\\" -and
    $_.FullName -notmatch "\\\\venv\\\\" -and
    $_.FullName -notmatch "\\\\.git\\\\"
}

$orphaned = @()

foreach ($dir in $pycacheDirs) {
    $parentDir = $dir.Parent
    $parentFiles = Get-ChildItem -Path $parentDir.FullName -Filter "*.py"
    if ($parentFiles.Count -eq 0) {
        $orphaned += $dir.FullName
        Write-Host "  ⚠️ Orphaned: $dir" -ForegroundColor Yellow
    }
}

if ($orphaned.Count -eq 0) {
    Write-Host "  ✅ No orphaned __pycache__ directories" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "  ⚠️ $($orphaned.Count) orphaned __pycache__ directory(ies)" -ForegroundColor Yellow
    Write-Host "     Run: Get-ChildItem -Path . -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force" -ForegroundColor Gray
}

Write-Host ""

# ============================================================
# Summary
# ============================================================

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$totalErrors = $missingInit.Count + $failedPackages.Count

if ($totalErrors -eq 0) {
    Write-Host "✅ STATUS: ALL VALIDATIONS PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ STATUS: $totalErrors ERROR(S) FOUND" -ForegroundColor Red
}

Write-Host ""