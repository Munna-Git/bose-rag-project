# Launch Bose RAG Application
# Windows PowerShell script

Write-Host "=" -NoNewline; Write-Host ("=" * 69)
Write-Host "Bose RAG Application Launcher"
Write-Host "=" -NoNewline; Write-Host ("=" * 69)
Write-Host ""

# Activate virtual environment
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..."
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "ERROR: Virtual environment not found!"
    Write-Host "Run: python -m venv venv"
    exit 1
}

# Launch application
Write-Host ""
python scripts\launch_app.py

# Deactivate on exit
deactivate
