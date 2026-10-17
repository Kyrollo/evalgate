@echo off
title EvalGate - LLM Quality & CI Gates
cls
echo ========================================================
echo       EvalGate - LLM Regression & Quality CI Gates
echo ========================================================
echo.
echo [1/3] Checking dependencies...
python -c "import uvicorn, fastapi" 2>nul || pip install fastapi uvicorn
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend && npm install && cd ..
)

echo [2/3] Starting Backend API (Port 8002)...
start "EvalGate API (Port 8002)" cmd /k "cd /d %~dp0backend && python -m uvicorn src.evalgate.main:app --port 8002 --reload"

echo [3/3] Starting Frontend UI (Port 3002)...
start "EvalGate UI (Port 3002)" cmd /k "cd /d %~dp0frontend && npm run dev"

timeout /t 3 /nobreak >nul
start http://localhost:3002
echo.
echo EvalGate is running!
echo   Frontend : http://localhost:3002
echo   Backend  : http://localhost:8002/docs
echo.
echo Press any key to stop all EvalGate processes...
pause >nul
taskkill /fi "WINDOWTITLE eq EvalGate API*" /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq EvalGate UI*" /f >nul 2>&1
echo Done.
