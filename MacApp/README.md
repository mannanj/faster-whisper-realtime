# Faster Whisper Realtime - Mac App

A minimal native macOS app wrapper for the Faster Whisper real-time transcription service.

## Features

- **Clean minimal UI**: No browser chrome, just your app with macOS window controls
- **WebKit-based**: Uses Safari's rendering engine (WKWebView)
- **Automatic server management**: Python Flask server starts/stops with app
- **Native macOS experience**: Standard traffic lights (close/minimize/maximize)

## Project Setup

### Method 1: Create Xcode Project Manually (Recommended)

1. Open Xcode
2. Create a new project: **File → New → Project**
3. Select **macOS → App**
4. Configure:
   - **Product Name**: `FasterWhisperRealtime`
   - **Team**: Your team
   - **Organization Identifier**: `com.yourname` (or any reverse domain)
   - **Interface**: `SwiftUI`
   - **Language**: `Swift`
   - **Uncheck** "Use Core Data"
   - **Uncheck** "Include Tests"
5. Save in `MacApp/` directory
6. Delete the default Swift files Xcode creates
7. **Add existing files to project**:
   - Right-click project in sidebar → "Add Files to..."
   - Select all `.swift` files from `FasterWhisperRealtime/` folder
   - Check "Copy items if needed"
8. **Add Python backend files to Resources**:
   - Select project in sidebar
   - Select target → "Build Phases" tab
   - Expand "Copy Bundle Resources"
   - Click "+" button
   - Add these files from parent directory:
     - `server.py`
     - `index.html`
     - `requirements.txt`
9. **Configure Info.plist**:
   - Replace default Info.plist with the one from `FasterWhisperRealtime/Info.plist`
10. **Build and Run** (⌘R)

### Method 2: Using Command Line (Alternative)

If you prefer command-line setup, you can use `xcodegen`:

```bash
brew install xcodegen
cd MacApp
xcodegen generate
open FasterWhisperRealtime.xcodeproj
```

(Note: You'll need to create a `project.yml` configuration file for xcodegen)

## App Structure

```
FasterWhisperRealtime.app/
├── Contents/
│   ├── Info.plist
│   ├── MacOS/
│   │   └── FasterWhisperRealtime (Swift executable)
│   ├── Resources/
│   │   ├── server.py          (Flask backend)
│   │   ├── index.html         (Web interface)
│   │   └── requirements.txt   (Python dependencies)
│   └── Frameworks/
```

## How It Works

1. **App Launch**: User double-clicks app
2. **Server Start**: AppDelegate starts Python server subprocess
3. **Health Check**: App polls `localhost:10000` until server responds
4. **Load UI**: WKWebView loads web interface
5. **User Interaction**: User interacts with web app in native window
6. **Quit**: User closes window → Server terminates gracefully

## Swift Files

### FasterWhisperRealtimeApp.swift
Main app entry point with SwiftUI `App` protocol and window configuration.

### AppDelegate.swift
Manages Python server lifecycle:
- Starts server subprocess on launch
- Monitors server health
- Terminates server on quit

### ContentView.swift
SwiftUI view containing WKWebView wrapper with loading state and retry logic.

## Development

### Running from Xcode
1. Make sure Python dependencies are installed in system Python:
   ```bash
   pip3 install -r requirements.txt
   ```
2. Press ⌘R to build and run
3. App will launch with embedded web interface

### Debugging
- Server logs appear in Xcode console
- Check server is running: `curl http://localhost:10000`
- Use Safari Web Inspector: Develop → Simulator → localhost

## Distribution

### Building for Release
1. Product → Archive
2. Distribute App → Copy App
3. Result: Standalone `.app` bundle

### Code Signing (Required for Distribution)
1. Select project → Signing & Capabilities
2. Choose your Team
3. Enable "Automatically manage signing"

### Notarization (Required for macOS 10.15+)
Follow Apple's notarization guide for distributing outside Mac App Store.

## Bundling Python Runtime (Optional)

For true standalone distribution without requiring system Python:

1. Use `relocatable-python` or `python-build-standalone`
2. Bundle in `Resources/python/`
3. Update AppDelegate to use bundled Python:
   ```swift
   let pythonPath = (resourcePath as NSString).appendingPathComponent("python/bin/python3")
   serverProcess?.executableURL = URL(fileURLWithPath: pythonPath)
   ```

## Requirements

- macOS 11.0+ (Big Sur or later)
- Xcode 13.0+
- Python 3.8+
- System Python with faster-whisper dependencies (or bundle Python runtime)

## Notes

- **First run**: faster-whisper downloads model (~150MB for base model)
- **Window style**: Hidden title bar with visible traffic lights
- **Server port**: Fixed at 10000 (configurable in server.py and ContentView.swift)
- **Microphone permission**: Automatically requested on first use
