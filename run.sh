#!/bin/bash

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Open browser after a short delay (in background)
(sleep 5 && open http://localhost:5000) &

# Open a new terminal window and run the server setup
osascript <<EOF
tell application "Terminal"
    do script "cd '$PROJECT_DIR' && bash -c '
echo \"🎙️  Faster Whisper Real-time Setup & Launch\"
echo \"============================================\"
echo \"\"

# Check if venv exists
if [ ! -d \"venv\" ]; then
    echo \"📦 Creating virtual environment...\"
    python3 -m venv venv
    if [ \$? -ne 0 ]; then
        echo \"❌ Failed to create virtual environment\"
        exit 1
    fi
    echo \"✅ Virtual environment created\"
    echo \"\"
fi

# Activate virtual environment
echo \"🔧 Activating virtual environment...\"
source venv/bin/activate

# Install/upgrade dependencies
echo \"📚 Installing dependencies...\"
pip install -q -r requirements.txt
if [ \$? -ne 0 ]; then
    echo \"❌ Failed to install dependencies\"
    exit 1
fi
echo \"✅ Dependencies installed\"
echo \"\"

# Run the server
echo \"🚀 Starting server...\"
echo \"\"
python3 server.py
'"
    activate
end tell
EOF

echo "🎙️  Opening new terminal window for server..."
echo "🌐 Browser will open automatically at http://localhost:5000"
