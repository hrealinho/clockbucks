#!/bin/bash

# Clock Bucks Quick Start Script

echo "🕒 Starting Clock Bucks - Meeting Cost Calculator"
echo "=================================================="

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

echo "✅ Python detected: $(python --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️  Setting up database..."
alembic upgrade head 2>/dev/null || echo "⚠️  No migrations to run (database already set up)"

echo ""
echo "🎯 Choose what you want to do:"
echo "1. Run development test (quick calculator demo)"
echo "2. Start API server"
echo "3. Run tests"
echo "4. Open API documentation"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🧪 Running development test..."
        python dev_test.py
        ;;
    2)
        echo "🚀 Starting API server..."
        echo "📍 API will be available at: http://127.0.0.1:8000"
        echo "📚 Documentation at: http://127.0.0.1:8000/docs"
        echo "💚 Health check at: http://127.0.0.1:8000/health"
        echo ""
        echo "Press Ctrl+C to stop the server"
        uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
        ;;
    3)
        echo "🧪 Running tests..."
        pytest tests/ -v
        ;;
    4)
        echo "🚀 Starting API server for documentation..."
        echo "📚 Opening documentation at: http://127.0.0.1:8000/docs"
        uvicorn src.main:app --reload --host 127.0.0.1 --port 8000 &
        sleep 3
        if command -v open &> /dev/null; then
            open http://127.0.0.1:8000/docs
        elif command -v xdg-open &> /dev/null; then
            xdg-open http://127.0.0.1:8000/docs
        else
            echo "Please open http://127.0.0.1:8000/docs in your browser"
        fi
        wait
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again and choose 1-4."
        exit 1
        ;;
esac

echo ""
echo "✨ Thanks for using Clock Bucks!"
