# ============================================================
# run_phase_b.ps1 - Execute All Phase B Validations
# ============================================================

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "PHASE B: Complete Validation Suite" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$scripts = @(
    "validate_packages.ps1",
    "validate_imports.ps1",
    "validate_syntax.ps1"
)

$allPassed = $true

foreach ($script in $scripts) {
    if (Test-Path $script) {
        Write-Host "Running: $script" -ForegroundColor Magenta
        & .\$script
        if ($LASTEXITCODE -ne 0) {
            $allPassed = $false
        }
        Write-Host ""
        Write-Host "-" * 80 -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host "⚠️ Script not found: $script" -ForegroundColor Yellow
    }
}

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "PHASE B: COMPLETE" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

if ($allPassed) {
    Write-Host "✅ All validations passed" -ForegroundColor Green
} else {
    Write-Host "❌ Some validations failed" -ForegroundColor Red
}

Write-Host ""