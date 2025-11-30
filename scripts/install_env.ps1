param(
    [string]$PythonExe = "python",
    [string]$VenvPath = "venv"
)

Write-Host "=== mainpipe: Windows PowerShell installer ===" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Split-Path -Parent $scriptDir
Set-Location -Path $projectRoot

Write-Host "`nStep 1/3: Creating virtual environment at '$VenvPath' (if not exists)..." -ForegroundColor Yellow
if (-Not (Test-Path $VenvPath)) {
    & $PythonExe -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment. Check that Python is installed and on PATH."
        exit 1
    }
} else {
    Write-Host "Virtual environment already exists. Skipping creation." -ForegroundColor DarkGray
}

Write-Host "`nStep 2/3: Activating virtual environment..." -ForegroundColor Yellow
$activateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
if (-Not (Test-Path $activateScript)) {
    Write-Error "Activation script not found at $activateScript"
    exit 1
}
. $activateScript

Write-Host "`nStep 3/3: Installing Python dependencies from requirements.txt..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Error "pip install failed. See output above for details."
    exit 1
}

Write-Host "`n[OK] Environment setup complete." -ForegroundColor Green
Write-Host "You can now run the pipeline with:" -ForegroundColor Green
Write-Host "  .\run_pipeline.bat" -ForegroundColor Green
