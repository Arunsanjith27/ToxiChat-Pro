@echo off
echo ============================================
echo  ToxiChat Pro - Setup and Launch
echo ============================================
echo.

echo [1/4] Installing backend dependencies...
cd /d "%~dp0backend"
pip install fastapi uvicorn "python-jose[cryptography]" motor pymongo dnspython python-dotenv joblib scikit-learn numpy pydantic python-multipart aiofiles certifi bcrypt redis 2>nul
echo.

echo [2/4] Installing frontend dependencies...
cd /d "%~dp0frontend"
call npm install 2>nul
echo.

echo [3/4] Starting backend on port 8000...
cd /d "%~dp0backend"
start "ToxiChat Backend" cmd /k "python main.py"
echo Backend starting...

echo [4/4] Starting frontend on port 3000...
cd /d "%~dp0frontend"
timeout /t 3 >nul
start "ToxiChat Frontend" cmd /k "npm start"
echo Frontend starting...

echo.
echo ============================================
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:3000
echo  API Docs: http://localhost:8000/docs
echo ============================================
echo.
pause
