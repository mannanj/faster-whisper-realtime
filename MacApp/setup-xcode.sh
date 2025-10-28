#!/bin/bash
set -e

echo "======================================"
echo "Faster Whisper Realtime - Mac App Setup"
echo "======================================"
echo ""

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Error: Xcode is not installed"
    echo "Please install Xcode from the Mac App Store"
    exit 1
fi

echo "✅ Xcode found"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3: brew install python3"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if pip requirements are installed
echo "Checking Python dependencies..."
cd ..
if python3 -c "import faster_whisper" 2>/dev/null; then
    echo "✅ faster-whisper is installed"
else
    echo "⚠️  faster-whisper not found"
    echo "Installing Python dependencies..."
    pip3 install -r requirements.txt
fi
echo ""

cd MacApp

# Instructions for manual Xcode project creation
echo "======================================"
echo "Next Steps - Create Xcode Project"
echo "======================================"
echo ""
echo "Since Xcode project files are binary/complex, please create the project manually:"
echo ""
echo "1. Open Xcode"
echo "2. File → New → Project"
echo "3. Select: macOS → App"
echo "4. Configure:"
echo "   - Product Name: FasterWhisperRealtime"
echo "   - Interface: SwiftUI"
echo "   - Language: Swift"
echo "   - Save in: $(pwd)"
echo ""
echo "5. After project is created:"
echo "   - Delete default ContentView.swift and FasterWhisperRealtimeApp.swift"
echo "   - Right-click project → Add Files to Project"
echo "   - Select all .swift files from FasterWhisperRealtime/"
echo ""
echo "6. Add backend files to Bundle Resources:"
echo "   - Select project → Build Phases → Copy Bundle Resources"
echo "   - Add: ../server.py, ../index.html, ../requirements.txt"
echo ""
echo "7. Build and Run (⌘R)"
echo ""
echo "======================================"
echo ""
echo "📁 Swift source files ready in: FasterWhisperRealtime/"
echo "📖 Full instructions in: README.md"
echo ""
