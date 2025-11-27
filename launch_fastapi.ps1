# Launch Bose RAG FastAPI Application
# Professional deployment script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Bose Professional Technical Assistant" -ForegroundColor Cyan
Write-Host "FastAPI Deployment" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
    if (-not $?) {
        Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
        Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
        exit 1
    }
}

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found" -ForegroundColor Red
    exit 1
}
Write-Host "SUCCESS: $pythonVersion" -ForegroundColor Green

# Check if Ollama is running
Write-Host "Checking Ollama service..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 5
    Write-Host "SUCCESS: Ollama is running" -ForegroundColor Green
    
    # Check if phi model exists
    $phiModel = $response.models | Where-Object { $_.name -like "phi*" }
    if ($phiModel) {
        Write-Host "SUCCESS: Phi model found ($($phiModel.name))" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Phi model not found" -ForegroundColor Yellow
        Write-Host "Run: ollama pull phi" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR: Ollama is not running" -ForegroundColor Red
    Write-Host "Please start Ollama first" -ForegroundColor Yellow
    exit 1
}

# Check if FastAPI and Uvicorn are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$packages = @("fastapi", "uvicorn")
foreach ($package in $packages) {
    $installed = pip show $package 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing $package..." -ForegroundColor Yellow
        pip install $package
    } else {
        Write-Host "SUCCESS: $package installed" -ForegroundColor Green
    }
}

# Check database
Write-Host "Checking vector database..." -ForegroundColor Yellow
if (Test-Path ".\data\vector_db") {
    $dbFiles = Get-ChildItem ".\data\vector_db" -Recurse | Measure-Object
    if ($dbFiles.Count -gt 0) {
        Write-Host "SUCCESS: Database found with content" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Database directory exists but is empty" -ForegroundColor Yellow
        Write-Host "Run: python scripts\demo.py to process documents" -ForegroundColor Yellow
    }
} else {
    Write-Host "WARNING: No database found" -ForegroundColor Yellow
    Write-Host "Run: python scripts\demo.py to process documents first" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Starting FastAPI Server..." -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Web Interface: http://localhost:8000" -ForegroundColor Green
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Yellow

# Start the FastAPI application
python app.py
