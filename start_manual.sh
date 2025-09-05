#!/bin/bash

echo "🚀 Starting User Profiler System (Manual Mode)"
echo "=============================================="

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Starting manually with Python venv..."
echo ""

# Backend
echo "🐍 Setting up Backend..."
cd "$SCRIPT_DIR/backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Setup environment file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

echo "Starting Backend API server..."
echo "Backend will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"

# Start backend using the same method as in testing
python -c "from src.api.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)" &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Frontend
echo ""
echo "🎨 Setting up Frontend..."
cd "$SCRIPT_DIR/frontend"

# Install npm dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install > /dev/null 2>&1
fi

echo "Starting Frontend development server..."
echo "Frontend will be available at: http://localhost:3000"

# Start frontend
npm run dev -- --host 0.0.0.0 --port 3000 &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 3

echo ""
echo "✅ System started successfully!"
echo "================================"
echo "📱 Frontend UI: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🧪 Health Check: http://localhost:8000/health"
echo ""
echo "💡 Tips:"
echo "  - Try crawling data for a user like 'testuser'"
echo "  - Check the timeline and profile pages"
echo "  - Configure OpenAI API key in backend/.env for LLM features"
echo ""
echo "Press Ctrl+C to stop both services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID