# ============================================================
# validate_syntax.ps1 - Python Syntax Validation
# ============================================================
# Checks: All project Python files have valid syntax using py_compile
# Filters out: venv, .venv, site-packages, .git, __pycache__, etc.
# ============================================================

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "PHASE B: Python Syntax Validation" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Project Root: $PWD" -ForegroundColor Yellow
Write-Host ""

# ============================================================
# 1. Compile All Application Python Files Only
# ============================================================

Write-Host "[1] Compiling project Python files..." -ForegroundColor Yellow
Write-Host "-" * 60 -ForegroundColor Gray

# Strict filter excluding virtual environments and third-party library files
$pyFiles = Get-ChildItem -Path . -Recurse -Filter "*.py" | Where-Object {
    $_.FullName -notmatch "\\venv\\" -and
    $_.FullName -notmatch "\\\.venv\\" -and
    $_.FullName -notmatch "\\site-packages\\" -and
    $_.FullName -notmatch "\\\.git\\" -and
    $_.FullName -notmatch "\\__pycache__\\" -and
    $_.FullName -notmatch "\\migrations\\versions\\" -and
    $_.FullName -notmatch "\\\.pytest_cache\\" -and
    $_.FullName -notmatch "\\\.mypy_cache\\"
}

$syntaxErrors = @()
$syntaxOk = @()

foreach ($file in $pyFiles) {
    $relPath = $file.FullName.Substring((Get-Location).Path.Length + 1)
    $result = python -m py_compile $file.FullName 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        $syntaxOk += $relPath
        Write-Host "  ✅ $relPath" -ForegroundColor Green
    } else {
        $syntaxErrors += "$relPath : $result"
        Write-Host "  ❌ $relPath" -ForegroundColor Red
        Write-Host "     $result" -ForegroundColor Red
    }
}

if ($syntaxErrors.Count -eq 0) {
    Write-Host ""
    Write-Host "  ✅ All $($syntaxOk.Count) project files compiled successfully" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "  ❌ $($syntaxErrors.Count) file(s) with syntax errors" -ForegroundColor Red
}

Write-Host ""

# ============================================================
# 2. Check for Stray/Orphaned .pyc Files in App Directory
# ============================================================

Write-Host "[2] Checking for stray .pyc files..." -ForegroundColor Yellow
Write-Host "-" * 60 -ForegroundColor Gray

$pycFiles = Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Where-Object {
    $_.FullName -notmatch "\\venv\\" -and
    $_.FullName -notmatch "\\\.venv\\" -and
    $_.FullName -notmatch "\\site-packages\\" -and
    $_.FullName -notmatch "\\\.git\\"
}

if ($pycFiles.Count -gt 0) {
    Write-Host "  ⚠️ $($pycFiles.Count) .pyc file(s) found in project folders" -ForegroundColor Yellow
} else {
    Write-Host "  ✅ No stray .pyc files found" -ForegroundColor Green
}

Write-Host ""

# ============================================================
# Summary
# ============================================================

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

if ($syntaxErrors.Count -eq 0) {
    Write-Host "✅ STATUS: ALL SYNTAX VALID" -ForegroundColor Green
    Write-Host "   $($syntaxOk.Count) project files validated"
} else {
    Write-Host "❌ STATUS: $($syntaxErrors.Count) SYNTAX ERROR(S)" -ForegroundColor Red
}

Write-Host ""