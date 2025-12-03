@echo off
REM Quick MCP Integration Test Script

echo ============================================================
echo MCP INTEGRATION TEST
echo ============================================================
echo.

echo Step 1: Checking if main server is running (port 8000)...
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Main server not running. Start with: python app.py
) else (
    echo ✓ Main server is running
)
echo.

echo Step 2: Starting MCP Server (port 8001)...
echo Note: This will start in a new window. Close it when done.
start "MCP Server" cmd /k "python mcp_server.py"
echo Waiting 10 seconds for server to initialize...
timeout /t 10 /nobreak >nul
echo.

echo Step 3: Testing MCP Server connection...
curl -s http://localhost:8001/ >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Failed to connect to MCP server
    echo   Make sure Python and dependencies are installed
    pause
    exit /b 1
) else (
    echo ✓ MCP Server is accessible
)
echo.

echo Step 4: Running MCP Client tests...
python mcp_client.py
echo.

echo ============================================================
echo MCP TEST COMPLETE
echo ============================================================
echo.
echo To manually stop MCP server, close its window or press Ctrl+C
pause
