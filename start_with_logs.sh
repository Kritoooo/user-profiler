#!/bin/bash

echo "🚀 Starting User Profiler System with Live Logs"
echo "=============================================="

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Starting manually with Python venv and live logs..."
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

# Create logs directory
mkdir -p logs

echo "Starting Backend API server with logging..."
echo "Backend will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Log Stream: http://localhost:8000/logs/recent"

# Start backend
python -c "from src.api.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')" &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start log monitoring in a separate terminal if possible
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal --title="User Profiler Logs" -- bash -c "
        cd '$SCRIPT_DIR/backend'
        echo '📋 Live Log Monitoring - User Profiler'
        echo '======================================'
        echo ''
        echo '📁 Log file: logs/user_profiler.log'
        echo '🌐 API logs: http://localhost:8000/logs/recent'
        echo ''
        echo 'Waiting for log file...'
        while [ ! -f 'logs/user_profiler.log' ]; do
            sleep 1
        done
        echo 'Log file found! Streaming logs...'
        echo ''
        tail -f logs/user_profiler.log | while IFS= read -r line; do
            echo \"\$(date '+%H:%M:%S') | \$line\"
        done
    "
elif command -v xterm &> /dev/null; then
    xterm -title "User Profiler Logs" -e "
        cd '$SCRIPT_DIR/backend'
        echo '📋 Live Log Monitoring - User Profiler'
        echo '======================================'
        echo ''
        while [ ! -f 'logs/user_profiler.log' ]; do
            sleep 1
        done
        tail -f logs/user_profiler.log
    " &
fi

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
echo "📋 Recent Logs: http://localhost:8000/logs/recent"
echo "🌊 Live Log Stream: http://localhost:8000/logs/stream"
echo "🧪 Health Check: http://localhost:8000/health"
echo ""
echo "💡 Log Monitoring:"
echo "  - Console logs: tail -f backend/logs/user_profiler.log"
echo "  - Web logs: curl http://localhost:8000/logs/recent"
echo "  - Live stream: curl http://localhost:8000/logs/stream"
echo ""
echo "🎯 Test the logging:"
echo "  curl -X POST http://localhost:8000/crawl -H 'Content-Type: application/json' -d '{\"user_id\":\"testuser\"}'"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    
    # Kill any log monitoring terminals
    pkill -f "tail -f logs/user_profiler.log" 2>/dev/null
    
    echo "✅ Services stopped"
    echo "📋 Logs saved in: backend/logs/user_profiler.log"
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Show real-time logs in the main terminal if no GUI terminal available
if ! command -v gnome-terminal &> /dev/null && ! command -v xterm &> /dev/null; then
    echo ""
    echo "📋 Showing live logs in this terminal..."
    echo "======================================="
    
    # Wait for log file to be created
    LOG_FILE="$SCRIPT_DIR/backend/logs/user_profiler.log"
    while [ ! -f "$LOG_FILE" ]; do
        sleep 1
        echo "Waiting for log file to be created..."
    done
    
    echo "Log file found! Streaming logs..."
    echo ""
    
    # Stream logs with colors
    tail -f "$LOG_FILE" &
    LOG_TAIL_PID=$!
    
    # Wait for processes
    wait $BACKEND_PID $FRONTEND_PID
else
    # Wait for processes without showing logs in main terminal
    wait $BACKEND_PID $FRONTEND_PID
fi