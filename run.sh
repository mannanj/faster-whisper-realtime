#!/bin/bash

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Function to display help
show_help() {
    echo "🎙️  Faster Whisper Real-time - Helper Script"
    echo "============================================"
    echo ""
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start                  - Setup and launch server"
    echo "  setup                  - Create venv and install dependencies only"
    echo "  stop                   - Stop server running on port 5000"
    echo "  help                   - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run.sh start        # Setup and start server"
    echo "  ./run.sh setup        # Only setup dependencies"
    echo "  ./run.sh stop         # Stop the server"
    echo ""
}

# Function to setup virtual environment and dependencies
setup_environment() {
    echo "🎙️  Faster Whisper Real-time Setup"
    echo "===================================="
    echo ""

    # Check if venv exists
    if [ ! -d "$PROJECT_DIR/venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv "$PROJECT_DIR/venv"
        if [ $? -ne 0 ]; then
            echo "❌ Failed to create virtual environment"
            exit 1
        fi
        echo "✅ Virtual environment created"
        echo ""
    else
        echo "✅ Virtual environment already exists"
        echo ""
    fi

    # Activate virtual environment
    echo "🔧 Activating virtual environment..."
    source "$PROJECT_DIR/venv/bin/activate"

    # Install/upgrade dependencies
    echo "📚 Installing dependencies..."
    pip install -q -r "$PROJECT_DIR/requirements.txt"
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
    echo ""
}

# Function to start the server
start_server() {
    # Open browser after a short delay (in background)
    (sleep 5 && open http://localhost:5000) &

    # Open a new terminal window and run the server
    osascript <<EOF
tell application "Terminal"
    do script "cd '$PROJECT_DIR' && source venv/bin/activate && echo '🚀 Starting server...' && echo '' && python3 server.py"
    activate
end tell
EOF

    echo "🎙️  Opening new terminal window for server..."
    echo "🌐 Browser will open automatically at http://localhost:5000"
}

# Function to stop the server
stop_server() {
    echo "🛑 Stopping Faster Whisper Real-time Server"
    echo "==========================================="
    echo ""

    # Find all processes using port 5000
    PIDS=$(lsof -ti:5000 2>/dev/null)

    if [ -z "$PIDS" ]; then
        echo "ℹ️  No process found running on port 5000"
        exit 0
    fi

    # Filter for Python/server.py processes only
    SERVER_PIDS=""
    OTHER_PIDS=""

    for PID in $PIDS; do
        # Check if it's a Python/server.py process
        if ps -p $PID -o args= 2>/dev/null | grep -q "python.*server.py"; then
            SERVER_PIDS="$SERVER_PIDS $PID"
        else
            OTHER_PIDS="$OTHER_PIDS $PID"
        fi
    done

    # Show what we found
    if [ ! -z "$SERVER_PIDS" ]; then
        echo "🔍 Found server.py process(es) on port 5000:"
        for PID in $SERVER_PIDS; do
            PROCESS_INFO=$(ps -p $PID -o pid=,args= 2>/dev/null)
            echo "   PID $PROCESS_INFO"
        done
        echo ""
    fi

    if [ ! -z "$OTHER_PIDS" ]; then
        echo "⚠️  Found other process(es) on port 5000 (will not kill):"
        for PID in $OTHER_PIDS; do
            PROCESS_INFO=$(ps -p $PID -o pid=,comm= 2>/dev/null)
            echo "   PID $PROCESS_INFO"
        done
        echo "   Note: On macOS, this is often AirPlay Receiver (ControlCenter)"
        echo "   Disable it in: System Preferences → General → AirDrop & Handoff"
        echo ""
    fi

    # If no server.py processes found, exit
    if [ -z "$SERVER_PIDS" ]; then
        echo "ℹ️  No server.py processes found to stop"
        exit 0
    fi

    # Kill server.py processes gracefully (SIGTERM)
    echo "🔪 Sending SIGTERM to server.py process(es)..."
    for PID in $SERVER_PIDS; do
        kill -TERM $PID 2>/dev/null && echo "   ✓ Sent SIGTERM to PID $PID"
    done

    # Wait a moment for graceful shutdown
    sleep 2

    # Check if any server.py processes are still running and force kill if needed
    REMAINING_PIDS=""
    for PID in $SERVER_PIDS; do
        if ps -p $PID > /dev/null 2>&1; then
            REMAINING_PIDS="$REMAINING_PIDS $PID"
        fi
    done

    if [ ! -z "$REMAINING_PIDS" ]; then
        echo "⚠️  Some processes still running, sending SIGKILL..."
        for PID in $REMAINING_PIDS; do
            kill -KILL $PID 2>/dev/null && echo "   ✓ Sent SIGKILL to PID $PID"
        done
    fi

    # Final verification
    sleep 1
    ALL_STOPPED=true
    for PID in $SERVER_PIDS; do
        if ps -p $PID > /dev/null 2>&1; then
            ALL_STOPPED=false
            break
        fi
    done

    echo ""
    if [ "$ALL_STOPPED" = true ]; then
        echo "✅ Server stopped successfully"
    else
        echo "❌ Failed to stop some processes. You may need to run with sudo."
    fi
}

# Main command handler
COMMAND=${1:-}

# If no command provided, show help
if [ -z "$COMMAND" ]; then
    show_help
    exit 0
fi

case "$COMMAND" in
    start)
        setup_environment
        start_server
        ;;
    setup)
        setup_environment
        echo "✅ Setup complete! Run './run.sh start' to launch the server."
        ;;
    stop)
        stop_server
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        echo ""
        show_help
        exit 1
        ;;
esac
