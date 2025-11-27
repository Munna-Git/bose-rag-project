@echo off
REM Launch Bose RAG FastAPI Application
REM Windows Batch Script (alternative to PowerShell)

echo ========================================
echo Bose Professional Technical Assistant
echo FastAPI Deployment
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check Python
echo Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

REM Check Ollama
echo Checking Ollama service...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ERROR: Ollama is not running
    echo Please start Ollama first
    pause
    exit /b 1
) else (
    echo SUCCESS: Ollama is running
)

REM Install FastAPI if needed
echo Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing fastapi...
    pip install fastapi uvicorn
)

pip show uvicorn >nul 2>&1
if errorlevel 1 (
    echo Installing uvicorn...
    pip install uvicorn
)

REM Check database
if exist "data\vector_db" (
    echo SUCCESS: Database found
) else (
    echo WARNING: No database found
    echo Run: python scripts\demo.py to process documents first
)

echo.
echo ========================================
echo Starting FastAPI Server...
echo ========================================
echo.
echo Web Interface: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Press Ctrl+C to stop
echo.

REM Start the application
python app.py
