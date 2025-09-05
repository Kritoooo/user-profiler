#!/bin/bash

echo "📋 User Profiler Log Viewer"
echo "=========================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/backend/logs/user_profiler.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ Log file not found: $LOG_FILE"
    echo ""
    echo "💡 The system needs to be running to generate logs."
    echo "   Try: ./start_with_logs.sh"
    exit 1
fi

echo "📁 Log file: $LOG_FILE"
echo "📊 File size: $(du -h "$LOG_FILE" | cut -f1)"
echo "📝 Total lines: $(wc -l < "$LOG_FILE")"
echo ""

# Check if argument provided
if [ "$1" = "follow" ] || [ "$1" = "-f" ]; then
    echo "🌊 Following live logs (Press Ctrl+C to exit)..."
    echo "=============================================="
    echo ""
    tail -f "$LOG_FILE" | while IFS= read -r line; do
        # Add timestamp if not already present
        if [[ $line != *"$(date +%Y-%m-%d)"* ]]; then
            echo "$(date '+%H:%M:%S') | $line"
        else
            echo "$line"
        fi
    done
elif [ "$1" = "recent" ] || [ "$1" = "-r" ]; then
    LINES=${2:-50}
    echo "📋 Last $LINES log entries:"
    echo "========================="
    echo ""
    tail -n $LINES "$LOG_FILE"
elif [ "$1" = "error" ] || [ "$1" = "-e" ]; then
    echo "🚨 Error logs:"
    echo "============="
    echo ""
    grep -i "error\|exception\|failed\|❌" "$LOG_FILE" | tail -20
elif [ "$1" = "user" ] || [ "$1" = "-u" ]; then
    if [ -z "$2" ]; then
        echo "❌ Please provide a user_id"
        echo "Usage: ./view_logs.sh user <user_id>"
        exit 1
    fi
    USER_ID="$2"
    echo "👤 Logs for user: $USER_ID"
    echo "======================"
    echo ""
    grep "user:$USER_ID" "$LOG_FILE" | tail -20
elif [ "$1" = "api" ] || [ "$1" = "-a" ]; then
    echo "🌐 API request logs:"
    echo "=================="
    echo ""
    grep -E "(POST|GET|PUT|DELETE)" "$LOG_FILE" | tail -20
elif [ "$1" = "help" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Usage: ./view_logs.sh [option] [args]"
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
    echo "  ./view_logs.sh follow          # Follow live logs"
    echo "  ./view_logs.sh recent 100      # Show last 100 lines"
    echo "  ./view_logs.sh user testuser   # Show logs for testuser"
    echo "  ./view_logs.sh error           # Show only errors"
    exit 0
else
    # Default: show recent logs and available options
    echo "📋 Recent log entries (last 30 lines):"
    echo "====================================="
    echo ""
    tail -n 30 "$LOG_FILE"
    echo ""
    echo "💡 Available options:"
    echo "  ./view_logs.sh follow     # Follow live logs"
    echo "  ./view_logs.sh recent 50  # Show last 50 lines"
    echo "  ./view_logs.sh error      # Show errors only"
    echo "  ./view_logs.sh help       # Show all options"
fi