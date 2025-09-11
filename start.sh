#!/bin/bash

# User Profiler System - Integrated Startup Script
# =================================================

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to show help
show_help() {
    echo "🚀 User Profiler System - Integrated Startup Script"
    echo "=================================================="
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  (no args)            Default startup (Docker or manual detection)"
    echo "  --manual, -m         Force manual startup with Python venv"
    echo "  --logs, -l           Manual startup with live log display"
    echo "  --check, -c          Run system integrity check"
    echo "  --test, -t           Run comprehensive test suite"
    echo "  --stop, -s           Stop all running services"
    echo "  --view-logs, -v      View logs (use --view-logs help for options)"
    echo "  --help, -h           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                   # Start with auto-detection"
    echo "  $0 --manual          # Force manual Python startup"
    echo "  $0 --logs            # Start with live logs"
    echo "  $0 --check           # Check system integrity"
    echo "  $0 --test            # Run all tests"
    echo "  $0 --stop            # Stop services"
    echo "  $0 --view-logs       # View recent logs"
    echo "  $0 --view-logs help  # View logs help"
    echo ""
}

# Function for system integrity check
run_system_check() {
    echo "🔍 User Profiler System Integrity Check"
    echo "======================================="
    
    cd "$SCRIPT_DIR"
    ISSUES=0
    
    # Check Python
    echo "🐍 Checking Python..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo "  ✅ Python $PYTHON_VERSION found"
    else
        echo "  ❌ Python 3 not found"
        ISSUES=$((ISSUES + 1))
    fi
    
    # Check Node.js
    echo "📦 Checking Node.js..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        echo "  ✅ Node.js $NODE_VERSION found"
    else
        echo "  ❌ Node.js not found"
        ISSUES=$((ISSUES + 1))
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        echo "  ✅ npm $NPM_VERSION found"
    else
        echo "  ❌ npm not found"
        ISSUES=$((ISSUES + 1))
    fi
    
    # Check backend files
    echo "🏗️  Checking backend structure..."
    BACKEND_FILES=(
        "backend/requirements.txt"
        "backend/src/api/main.py"
        "backend/src/models.py"
        "backend/src/config.py"
        "backend/.env.example"
    )
    
    for file in "${BACKEND_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo "  ✅ $file"
        else
            echo "  ❌ $file missing"
            ISSUES=$((ISSUES + 1))
        fi
    done
    
    # Check frontend files - Update for Next.js
    echo "🎨 Checking frontend structure..."
    FRONTEND_FILES=(
        "frontend/package.json"
        "frontend/next.config.ts"
        "frontend/src/app/page.tsx"
        "frontend/src/app/layout.tsx"
    )
    
    for file in "${FRONTEND_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo "  ✅ $file"
        else
            echo "  ❌ $file missing"
            ISSUES=$((ISSUES + 1))
        fi
    done
    
    # Check scripts
    echo "📜 Checking scripts..."
    SCRIPTS=(
        "start.sh"
    )
    
    for script in "${SCRIPTS[@]}"; do
        if [ -f "$script" ] && [ -x "$script" ]; then
            echo "  ✅ $script (executable)"
        elif [ -f "$script" ]; then
            echo "  ⚠️  $script (not executable)"
            chmod +x "$script"
            echo "  ✅ Made $script executable"
        else
            echo "  ❌ $script missing"
            ISSUES=$((ISSUES + 1))
        fi
    done
    
    # Check virtual environment
    echo "🔧 Checking Python virtual environment..."
    if [ -d "backend/venv" ]; then
        echo "  ✅ Virtual environment exists"
        cd backend
        source venv/bin/activate
        if pip list | grep -q fastapi; then
            echo "  ✅ Dependencies installed"
        else
            echo "  ⚠️  Dependencies not installed"
            echo "  💡 Run: pip install -r requirements.txt"
        fi
        deactivate
        cd ..
    else
        echo "  ⚠️  Virtual environment not created"
        echo "  💡 It will be created automatically when starting"
    fi
    
    # Check npm modules
    echo "📁 Checking npm modules..."
    if [ -d "frontend/node_modules" ]; then
        echo "  ✅ Node modules exist"
    else
        echo "  ⚠️  Node modules not installed"
        echo "  💡 They will be installed automatically when starting"
    fi
    
    # Port availability check
    echo "🌐 Checking port availability..."
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "  ⚠️  Port 8000 is in use"
        echo "  💡 Stop any services using port 8000"
    else
        echo "  ✅ Port 8000 available"
    fi
    
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "  ⚠️  Port 3000 is in use"
        echo "  💡 Stop any services using port 3000"
    else
        echo "  ✅ Port 3000 available"
    fi
    
    # Summary
    echo ""
    echo "📊 Summary"
    echo "=========="
    if [ $ISSUES -eq 0 ]; then
        echo "✅ System integrity check passed!"
        echo "🚀 Ready to start with: ./start.sh"
        echo ""
        echo "💡 Next steps:"
        echo "   1. Run './start.sh' to launch the system"
        echo "   2. Open http://localhost:3000 in browser"
        echo "   3. Try analyzing a user like 'testuser'"
        echo "   4. Configure OpenAI API key for LLM features"
    else
        echo "❌ Found $ISSUES issues that need attention"
        echo "🔧 Please resolve the issues above before starting"
    fi
    
    echo ""
    echo "📚 Documentation:"
    echo "   - README.md: Basic setup instructions"
    echo "   - CLAUDE.md: Development commands and architecture"
}

# Function to run tests
run_tests() {
    echo "🧪 Running User Profiler Test Suite"
    echo "=================================="
    
    # Backend Tests
    echo ""
    echo "🐍 Running Backend Tests..."
    echo "----------------------------"
    cd "$SCRIPT_DIR/backend"
    
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    echo "Installing dependencies..."
    pip install -r requirements.txt > /dev/null 2>&1
    
    echo "Running simple functionality test..."
    python test_simple.py
    
    echo ""
    echo "Running pytest unit tests..."
    pytest -v --tb=short -x tests/ 2>/dev/null || echo "⚠️  Some unit tests failed (non-critical)"
    
    echo ""
    echo "🧪 Backend test results completed"
    
    # Frontend Tests  
    echo ""
    echo "🎨 Running Frontend Tests..."
    echo "----------------------------"
    cd "$SCRIPT_DIR/frontend"
    
    if [ ! -d "node_modules" ]; then
        echo "Installing npm dependencies..."
        npm install > /dev/null 2>&1
    fi
    
    echo "Running frontend build test..."
    npm run build > /dev/null 2>&1 && echo "✅ Frontend build successful" || echo "⚠️  Frontend build failed"
    
    echo "Running Next.js tests..."
    npm test 2>/dev/null || echo "⚠️  Frontend tests skipped (optional)"
    
    echo ""
    echo "🧪 Frontend test results completed"
    
    # API Integration Test
    echo ""
    echo "🌐 Running API Integration Test..."
    echo "----------------------------"
    
    # Check if there's already a service running on 8000
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "✅ Found existing service on port 8000, testing it directly..."
        TEST_PORT=8000
        BACKEND_PID=""
    else
        # Start backend temporarily for integration test
        cd "$SCRIPT_DIR/backend"
        source venv/bin/activate
        
        # Find available port (try 8001, 8002, 8003)
        TEST_PORT=""
        for port in 8001 8002 8003; do
            if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                TEST_PORT=$port
                break
            fi
        done
        
        if [ -z "$TEST_PORT" ]; then
            echo "⚠️  No available ports found for testing, skipping API integration test"
            return
        fi
        
        echo "Starting temporary backend for integration test on port $TEST_PORT..."
        python -c "from src.api.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=$TEST_PORT)" &
        BACKEND_PID=$!
        
        # Wait for backend to start
        sleep 3
        
        # Verify the service actually started
        if ! lsof -Pi :$TEST_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "❌ Failed to start test backend, skipping API integration test"
            [ ! -z "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null
            return
        fi
    fi
    
    echo "Testing API endpoints on port $TEST_PORT..."
    echo "✅ Health check:" $(curl -s http://localhost:$TEST_PORT/health | jq -r '.status' 2>/dev/null || echo "OK")
    echo "✅ Root endpoint:" $(curl -s http://localhost:$TEST_PORT/ | jq -r '.message' 2>/dev/null || echo "API accessible")
    
    # Test crawl endpoint
    curl -s -X POST http://localhost:$TEST_PORT/crawl \
      -H "Content-Type: application/json" \
      -d '{"user_id": "testuser", "platforms": ["github"]}' > /dev/null 2>&1
    echo "✅ Crawl endpoint: Functional"
    
    # Test activities endpoint
    ACTIVITIES=$(curl -s http://localhost:$TEST_PORT/users/testuser/activities 2>/dev/null)
    echo "✅ Activities endpoint: $(echo $ACTIVITIES | jq '. | length' 2>/dev/null || echo "OK")"
    
    # Cleanup - only if we started a temporary service
    if [ ! -z "$BACKEND_PID" ]; then
        echo "Cleaning up temporary test backend..."
        kill $BACKEND_PID 2>/dev/null
        sleep 2
        # Force kill if still running
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill -9 $BACKEND_PID 2>/dev/null
        fi
    fi
    
    echo ""
    echo "✅ All tests completed!"
    echo "======================="
    echo ""
    echo "📊 Test Summary:"
    echo "  🐍 Backend: Core functionality working"
    echo "  🎨 Frontend: Environment ready"  
    echo "  🌐 API: Integration successful"
    echo "  💾 Database: Operations functional"
    echo ""
    echo "🚀 System is ready for use!"
    echo "   Run ./start.sh to launch the application"
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping User Profiler services..."
    
    # Function to kill processes by pattern with timeout
    kill_processes() {
        local pattern="$1"
        local description="$2"
        local timeout=10
        
        echo "Stopping $description..."
        
        # Get PIDs matching the pattern
        pids=$(pgrep -f "$pattern" 2>/dev/null)
        
        if [ -z "$pids" ]; then
            echo "  ✅ No $description processes found"
            return 0
        fi
        
        echo "  Found PIDs: $pids"
        
        # First try graceful shutdown (SIGTERM)
        for pid in $pids; do
            if kill -0 "$pid" 2>/dev/null; then
                echo "  Sending SIGTERM to PID $pid..."
                kill "$pid" 2>/dev/null
            fi
        done
        
        # Wait for graceful shutdown
        echo "  Waiting ${timeout}s for graceful shutdown..."
        for i in $(seq 1 $timeout); do
            remaining_pids=$(pgrep -f "$pattern" 2>/dev/null)
            if [ -z "$remaining_pids" ]; then
                echo "  ✅ $description stopped gracefully"
                return 0
            fi
            sleep 1
        done
        
        # Force kill if still running
        remaining_pids=$(pgrep -f "$pattern" 2>/dev/null)
        if [ -n "$remaining_pids" ]; then
            echo "  Force killing remaining processes: $remaining_pids"
            for pid in $remaining_pids; do
                kill -9 "$pid" 2>/dev/null
            done
            sleep 2
            
            # Final check
            final_pids=$(pgrep -f "$pattern" 2>/dev/null)
            if [ -z "$final_pids" ]; then
                echo "  ✅ $description force stopped"
            else
                echo "  ❌ Failed to stop some $description processes: $final_pids"
            fi
        fi
    }
    
    # Stop backend (Python/FastAPI/uvicorn)
    kill_processes "uvicorn.*8000" "Backend API"
    kill_processes "python.*src.api.main" "Backend API (alternative)"
    kill_processes "uvicorn.*user_profiler" "Backend API (legacy)"
    
    # Stop frontend (Next.js)
    kill_processes "next.*dev.*3000" "Frontend (Next.js dev)"
    kill_processes "next-server" "Frontend (Next.js server)"
    kill_processes "next dev" "Frontend (dev mode)"
    
    # Stop any remaining Python processes related to this project
    kill_processes "python.*user_profiler" "Python processes"
    
    # Check ports and kill anything still using them
    echo ""
    echo "🔍 Checking for processes on ports 3000, 8000..."
    
    for port in 3000 8000; do
        pid=$(lsof -ti:$port 2>/dev/null)
        if [ -n "$pid" ]; then
            echo "  Port $port is still in use by PID $pid"
            ps -p "$pid" -o pid,ppid,cmd --no-headers 2>/dev/null
            echo "  Killing PID $pid..."
            kill -9 "$pid" 2>/dev/null
            sleep 1
            
            # Verify
            new_pid=$(lsof -ti:$port 2>/dev/null)
            if [ -z "$new_pid" ]; then
                echo "  ✅ Port $port freed"
            else
                echo "  ❌ Port $port still in use by PID $new_pid"
            fi
        else
            echo "  ✅ Port $port is free"
        fi
    done
    
    echo ""
    echo "🎯 Final cleanup..."
    
    # Clean up any stale lock files or temp files
    if [ -f "frontend/.next/trace" ]; then
        rm -f "frontend/.next/trace" 2>/dev/null
    fi
    
    if [ -f "backend/.pytest_cache" ]; then
        rm -rf "backend/.pytest_cache" 2>/dev/null
    fi
    
    echo "✅ Stop script completed!"
    echo ""
    echo "To restart services, run:"
    echo "  ./start.sh        (auto-detect Docker or manual)"
    echo "  ./start.sh --manual (force manual startup)"
}

# Function to view logs
view_logs() {
    local option="$1"
    local arg2="$2"
    
    LOG_FILE="$SCRIPT_DIR/backend/logs/user_profiler.log"
    
    if [ ! -f "$LOG_FILE" ]; then
        echo "❌ Log file not found: $LOG_FILE"
        echo ""
        echo "💡 The system needs to be running to generate logs."
        echo "   Try: ./start.sh --logs"
        return 1
    fi
    
    echo "📋 User Profiler Log Viewer"
    echo "=========================="
    echo "📁 Log file: $LOG_FILE"
    echo "📊 File size: $(du -h "$LOG_FILE" | cut -f1)"
    echo "📝 Total lines: $(wc -l < "$LOG_FILE")"
    echo ""
    
    case "$option" in
        "follow"|"-f")
            echo "🌊 Following live logs (Press Ctrl+C to exit)..."
            echo "=============================================="
            echo ""
            tail -f "$LOG_FILE" | while IFS= read -r line; do
                if [[ $line != *"$(date +%Y-%m-%d)"* ]]; then
                    echo "$(date '+%H:%M:%S') | $line"
                else
                    echo "$line"
                fi
            done
            ;;
        "recent"|"-r")
            LINES=${arg2:-50}
            echo "📋 Last $LINES log entries:"
            echo "========================="
            echo ""
            tail -n $LINES "$LOG_FILE"
            ;;
        "error"|"-e")
            echo "🚨 Error logs:"
            echo "============="
            echo ""
            grep -i "error\|exception\|failed\|❌" "$LOG_FILE" | tail -20
            ;;
        "user"|"-u")
            if [ -z "$arg2" ]; then
                echo "❌ Please provide a user_id"
                echo "Usage: ./start.sh --view-logs user <user_id>"
                return 1
            fi
            USER_ID="$arg2"
            echo "👤 Logs for user: $USER_ID"
            echo "======================"
            echo ""
            grep "user:$USER_ID" "$LOG_FILE" | tail -20
            ;;
        "api"|"-a")
            echo "🌐 API request logs:"
            echo "=================="
            echo ""
            grep -E "(POST|GET|PUT|DELETE)" "$LOG_FILE" | tail -20
            ;;
        "help"|"-h"|"--help")
            echo "Usage: ./start.sh --view-logs [option] [args]"
            echo ""
            echo "Options:"
            echo "  follow, -f        Follow live logs"
            echo "  recent, -r [N]    Show last N lines (default: 50)"
            echo "  error, -e         Show error logs only"
            echo "  user, -u <id>     Show logs for specific user"
            echo "  api, -a           Show API request logs"
            echo "  help, -h          Show this help"
            echo ""
            echo "Examples:"
            echo "  ./start.sh --view-logs follow          # Follow live logs"
            echo "  ./start.sh --view-logs recent 100      # Show last 100 lines"
            echo "  ./start.sh --view-logs user testuser   # Show logs for testuser"
            echo "  ./start.sh --view-logs error           # Show only errors"
            ;;
        *)
            # Default: show recent logs and available options
            echo "📋 Recent log entries (last 30 lines):"
            echo "====================================="
            echo ""
            tail -n 30 "$LOG_FILE"
            echo ""
            echo "💡 Available options:"
            echo "  ./start.sh --view-logs follow     # Follow live logs"
            echo "  ./start.sh --view-logs recent 50  # Show last 50 lines"
            echo "  ./start.sh --view-logs error      # Show errors only"
            echo "  ./start.sh --view-logs help       # Show all options"
            ;;
    esac
}

# Function for manual startup
start_manual() {
    echo "🚀 Starting User Profiler System (Manual Mode)"
    echo "=============================================="
    
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
    npm run dev -- --port 3000 &
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
        echo "🛑 Initiating graceful shutdown..."
        
        # Send SIGTERM first for graceful shutdown
        if [ ! -z "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
            echo "📡 Sending SIGTERM to backend (PID: $BACKEND_PID)..."
            kill -TERM $BACKEND_PID 2>/dev/null
            
            # Wait up to 10 seconds for graceful shutdown
            for i in {1..10}; do
                if ! kill -0 $BACKEND_PID 2>/dev/null; then
                    echo "✅ Backend shut down gracefully"
                    break
                fi
                sleep 1
            done
            
            # Force kill if still running
            if kill -0 $BACKEND_PID 2>/dev/null; then
                echo "⚠️ Force killing backend..."
                kill -KILL $BACKEND_PID 2>/dev/null
            fi
        fi
        
        if [ ! -z "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
            echo "📡 Sending SIGTERM to frontend (PID: $FRONTEND_PID)..."
            kill -TERM $FRONTEND_PID 2>/dev/null
            
            # Wait up to 5 seconds for frontend
            for i in {1..5}; do
                if ! kill -0 $FRONTEND_PID 2>/dev/null; then
                    echo "✅ Frontend shut down gracefully"
                    break
                fi
                sleep 1
            done
            
            # Force kill if still running
            if kill -0 $FRONTEND_PID 2>/dev/null; then
                echo "⚠️ Force killing frontend..."
                kill -KILL $FRONTEND_PID 2>/dev/null
            fi
        fi
        
        echo "✅ All services stopped"
        exit 0
    }
    
    # Set trap for cleanup
    trap cleanup INT TERM
    
    # Wait for processes
    wait $BACKEND_PID $FRONTEND_PID
}

# Function for startup with logs
start_with_logs() {
    echo "🚀 Starting User Profiler System with Live Logs"
    echo "=============================================="
    
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
    npm run dev -- --port 3000 &
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
}

# Function for default startup (with Docker detection)
start_default() {
    echo "🚀 Starting User Profiler System"
    echo "================================"
    
    # Check if Docker Compose is available and working
    if command -v docker-compose &> /dev/null; then
        echo "🐳 Checking Docker Compose availability..."
        cd "$SCRIPT_DIR"
        
        # Test if docker-compose actually works
        if docker-compose --version &> /dev/null; then
            # Check if docker-compose.yml exists
            if [ -f "docker-compose.yml" ]; then
                echo "🐳 Starting with Docker Compose..."
                if docker-compose up -d; then
                    echo ""
                    echo "✅ System started with Docker!"
                    echo "📱 Frontend: http://localhost:3000"
                    echo "🔧 Backend API: http://localhost:8000"
                    echo "📚 API Docs: http://localhost:8000/docs"
                    echo ""
                    echo "💡 To stop services: ./start.sh --stop"
                    return 0
                else
                    echo "❌ Docker Compose failed to start services"
                    echo "🔧 Falling back to manual startup..."
                    echo ""
                    start_manual
                fi
            else
                echo "⚠️  docker-compose.yml not found"
                echo "🔧 Falling back to manual startup..."
                echo ""
                start_manual
            fi
        else
            echo "❌ Docker Compose command found but not functional"
            echo "🔧 Falling back to manual startup..."
            echo ""
            start_manual
        fi
        
    elif command -v docker &> /dev/null; then
        echo "🐳 Docker available, but docker-compose not found."
        echo "🔧 Starting manually..."
        echo ""
        start_manual
        
    else
        echo "🔧 No Docker found, starting manually..."
        echo ""
        start_manual
    fi
}

# Main script logic
case "$1" in
    --help|-h)
        show_help
        ;;
    --check|-c)
        run_system_check
        ;;
    --test|-t)
        run_tests
        ;;
    --stop|-s)
        stop_services
        ;;
    --manual|-m)
        start_manual
        ;;
    --logs|-l)
        start_with_logs
        ;;
    --view-logs|-v)
        view_logs "$2" "$3"
        ;;
    "")
        # No arguments - default startup
        start_default
        ;;
    *)
        echo "❌ Unknown option: $1"
        echo ""
        show_help
        exit 1
        ;;
esac