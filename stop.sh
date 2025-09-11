#!/bin/bash

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
kill_processes "uvicorn.*user_profiler" "Backend API"
kill_processes "python.*src.api.main" "Backend API (alternative)"

# Stop frontend (Next.js)
kill_processes "next-server" "Frontend"
kill_processes "next dev" "Frontend (dev mode)"

# Stop any remaining Python processes related to this project
kill_processes "python.*user_profiler" "Python processes"

# Check ports and kill anything still using them
echo ""
echo "🔍 Checking for processes on ports 3000, 3001, 8000..."

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
echo "  ./start_manual.sh (force manual startup)"