#!/bin/bash
# Helper script to start the backend with proper environment setup

echo "🚀 Starting ClauseBot Backend..."

cd backend/clausebot-api

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies if requirements.txt is newer than last install
if [ requirements.txt -nt .venv/pyvenv.cfg ] || [ ! -f .venv/installed.flag ]; then
    echo "📚 Installing dependencies..."
    pip install -r requirements.txt
    touch .venv/installed.flag
fi

# Start the server
echo "🌐 Starting FastAPI server..."
echo "   API will be available at: http://localhost:8000"
echo "   Health check: http://localhost:8000/health"
echo "   Agent memory stats: http://localhost:8000/v1/agent/memory/stats"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn clausebot_api.main:app --reload --host 0.0.0.0 --port 8000
