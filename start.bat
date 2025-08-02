@echo off
REM Clock Bucks Quick Start Script for Windows

echo 🕒 Starting Clock Bucks - Meeting Cost Calculator
echo ==================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.11+ first.
    pause
    exit /b 1
)

echo ✅ Python detected: 
python --version

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Run database migrations
echo 🗄️  Setting up database...
alembic upgrade head 2>nul || echo ⚠️  No migrations to run (database already set up)

echo.
echo 🎯 Choose what you want to do:
echo 1. Run development test (quick calculator demo)
echo 2. Start API server
echo 3. Run tests
echo 4. Open API documentation
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo 🧪 Running development test...
    python dev_test.py
) else if "%choice%"=="2" (
    echo 🚀 Starting API server...
    echo 📍 API will be available at: http://127.0.0.1:8000
    echo 📚 Documentation at: http://127.0.0.1:8000/docs
    echo 💚 Health check at: http://127.0.0.1:8000/health
    echo.
    echo Press Ctrl+C to stop the server
    uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
) else if "%choice%"=="3" (
    echo 🧪 Running tests...
    pytest tests/ -v
) else if "%choice%"=="4" (
    echo 🚀 Starting API server for documentation...
    echo 📚 Opening documentation at: http://127.0.0.1:8000/docs
    start http://127.0.0.1:8000/docs
    uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
) else (
    echo ❌ Invalid choice. Please run the script again and choose 1-4.
    pause
    exit /b 1
)

echo.
echo ✨ Thanks for using Clock Bucks!
pause
