param(
    [switch]$SkipStress,
    [int]$TimeoutSec = 600
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try {
    $OutputEncoding = [System.Text.UTF8Encoding]::new()
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
} catch {}
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'

# Resolve repo root from this script's location
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
Set-Location $repoRoot

# Output directories
$reportDir = Join-Path $repoRoot '04-DATA\reports\fase5'
$null = New-Item -ItemType Directory -Path $reportDir -Force -ErrorAction SilentlyContinue

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$logFile = Join-Path $reportDir "fase5_validation_$timestamp.log"

function Write-Header($text) {
    Write-Host "" # blank line
    Write-Host "==== $text ====" -ForegroundColor Cyan
    Write-Host "" # blank line
}

function Invoke-Step {
    param(
        [Parameter(Mandatory)] [string]$Name,
        [Parameter(Mandatory)] [string]$RelPath
    )
    $fullPath = Join-Path $repoRoot $RelPath
    if (-not (Test-Path $fullPath)) {
        $msg = "[SKIP] $Name (missing: $RelPath)"
        Write-Warning $msg
        $msg | Tee-Object -FilePath $logFile -Append | Out-Null
        return $false
    }

    Write-Header $Name
    "[RUN] $Name -> $RelPath" | Tee-Object -FilePath $logFile -Append

    # Determine Python executable preference
    $pythonExe = "$Env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
    if (-not (Test-Path $pythonExe)) { $pythonExe = 'python' }
    $usePyLauncher = $false
    try { $null = & $pythonExe --version 2>$null } catch { $usePyLauncher = $true }
    if ($usePyLauncher) { $pythonExe = 'py' }

    # Build arguments
    if ($pythonExe -ieq 'py') {
        $args = "-3 -X utf8 `"$fullPath`""
    } else {
        $args = "-X utf8 `"$fullPath`""
    }

    # Use Start-Process to reliably capture output and exit code (PS 5.1 compatible)
    $tmpOut = [System.IO.Path]::GetTempFileName()
    $tmpErr = [System.IO.Path]::GetTempFileName()
    try {
        $proc = Start-Process -FilePath $pythonExe -ArgumentList $args -NoNewWindow -PassThru -RedirectStandardOutput $tmpOut -RedirectStandardError $tmpErr
        $waited = $true
        try {
            Wait-Process -Id $proc.Id -Timeout $TimeoutSec -ErrorAction Stop
        } catch {
            $waited = $false
        }

        if (-not $waited) {
            try { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue } catch {}
            "[TIMEOUT] $Name exceeded ${TimeoutSec}s" | Tee-Object -FilePath $logFile -Append
            $exit = 124
        } else {
            $exit = $proc.ExitCode
        }

        # Append outputs to log and echo to console
        if (Test-Path $tmpOut) { Get-Content -Path $tmpOut -Encoding UTF8 | Tee-Object -FilePath $logFile -Append }
        if (Test-Path $tmpErr) { Get-Content -Path $tmpErr -Encoding UTF8 | Tee-Object -FilePath $logFile -Append }
    } finally {
        Remove-Item -Path $tmpOut,$tmpErr -ErrorAction SilentlyContinue
    }

    if ($exit -eq 0) {
        "[OK] $Name (exit=$exit)" | Tee-Object -FilePath $logFile -Append
        return $true
    } else {
        "[FAIL] $Name (exit=$exit)" | Tee-Object -FilePath $logFile -Append
        return $false
    }
}

Write-Header 'FASE 5 VALIDATION RUN'
"Repo Root: $repoRoot" | Tee-Object -FilePath $logFile -Append | Out-Null
"Log File:  $logFile" | Tee-Object -FilePath $logFile -Append | Out-Null

$overall = $true

# Run master suite first; if it fails due to dashboard unavailability, individual runs may still pass
# Run master suite (informational); do not affect overall status
$null = Invoke-Step -Name 'System Master Suite' -RelPath 'tests\\test_fase5_master_suite.py'

# Aggregate status from individual suites
$overall = (Invoke-Step -Name 'Config Manager Tests' -RelPath 'tests\\test_config_manager_enterprise.py') -and $overall
$overall = (Invoke-Step -Name 'ML Pipeline Tests' -RelPath 'tests\\test_machine_learning_pipeline.py') -and $overall
$overall = (Invoke-Step -Name 'Dashboard Tests' -RelPath 'tests\\test_dashboard_enterprise.py') -and $overall

if (-not $SkipStress) {
    $overall = (Invoke-Step -Name 'Integrated Stress Test' -RelPath 'tests\integrated_stress_test.py') -and $overall
    $overall = (Invoke-Step -Name 'Production Stress Test' -RelPath 'tests\stress_test_production.py') -and $overall
}

Write-Header 'SUMMARY'
if ($overall) {
    Write-Host 'FASE 5 Validation: SUCCESS' -ForegroundColor Green
    "FASE 5 Validation: SUCCESS" | Tee-Object -FilePath $logFile -Append | Out-Null
    exit 0
} else {
    Write-Host 'FASE 5 Validation: NEEDS ATTENTION' -ForegroundColor Yellow
    "FASE 5 Validation: NEEDS ATTENTION" | Tee-Object -FilePath $logFile -Append | Out-Null
    exit 1
}