# Task 20: Convert to Native Mac App with Embedded WebView

- [ ] Create SwiftUI Mac app project with WKWebView
- [ ] Implement minimal borderless window (only macOS traffic lights)
- [ ] Add Python server lifecycle management
- [ ] Bundle Python runtime and dependencies in app Resources
- [ ] Design app icon and Info.plist configuration
- [ ] Add graceful shutdown handling (stop server on quit)
- [ ] Package for distribution (optional: code signing)
- **Location:** `MacApp/`, `server.py`

## Context

Convert the Flask-based web application into a standalone macOS application that:
1. Uses **SwiftUI + WKWebView** to display the Flask web interface natively
2. Provides a **minimal, clean UI** - no browser chrome, just app content
3. Shows only **macOS window controls** (close, minimize, maximize)
4. Automatically manages Python server lifecycle (start/stop)
5. Bundles Python backend with faster-whisper runtime

## Design Approach: SwiftUI + WKWebView Wrapper

**Why this approach:**
- **Minimal bloat**: No browser UI elements (no address bar, tabs, bookmarks)
- **Native macOS**: Uses Safari's WebKit engine but in a clean native window
- **Small footprint**: Swift app is tiny, Python backend runs as subprocess
- **Professional**: Standard macOS window with traffic light controls
- **Fast**: Direct WKWebView rendering without browser overhead

## App Structure

```
FasterWhisperRealtime.app/
├── Contents/
│   ├── Info.plist
│   ├── MacOS/
│   │   └── FasterWhisperRealtime (Swift executable)
│   ├── Resources/
│   │   ├── icon.icns
│   │   ├── python/           (bundled Python runtime)
│   │   ├── requirements.txt
│   │   ├── server.py
│   │   ├── index.html
│   │   └── run.sh
│   └── Frameworks/           (Swift/WebKit frameworks)
```

## Technical Implementation

### Swift App Components

**1. Main App Structure:**
- SwiftUI `App` with single `WindowGroup`
- Custom window style: `.hiddenTitleBar()` with traffic lights visible
- WKWebView wrapper loading `http://localhost:10000`

**2. Server Management:**
- Launch Python subprocess on app start: `python3 server.py`
- Monitor server health (poll localhost:10000 until ready)
- Terminate subprocess on app quit
- Handle port conflicts gracefully

**3. Window Configuration:**
- Fixed or resizable window (user preference)
- No title bar text (clean minimal look)
- Standard macOS traffic light buttons (top-left)
- Optional: remember window size/position

### Python Backend Integration

**Bundling Strategy:**
- Include Python 3.x runtime in `Resources/python/`
- Copy `server.py`, `index.html`, `requirements.txt` to Resources
- Use `pip install` on first launch to install dependencies
- Or: pre-bundle venv with all dependencies

**Server Lifecycle:**
1. App launches → Start Python server subprocess
2. Wait for server ready (HTTP 200 on localhost:10000)
3. Load WKWebView with `http://localhost:10000`
4. User quits app → Send SIGTERM to Python process
5. Clean shutdown

## Implementation Steps

1. **Create Xcode project** (macOS App, SwiftUI, Swift)
2. **Implement WKWebView wrapper** with minimal window chrome
3. **Add Python subprocess management** (Process API)
4. **Bundle Python runtime and dependencies**
5. **Configure Info.plist** with app metadata and permissions
6. **Design app icon** (.icns file)
7. **Test on clean macOS system**
8. **Package for distribution** (DMG or ZIP)

## Code Outline

### ContentView.swift
```swift
import SwiftUI
import WebKit

struct ContentView: View {
    var body: some View {
        WebView(url: URL(string: "http://localhost:10000")!)
            .frame(minWidth: 800, minHeight: 600)
    }
}

struct WebView: NSViewRepresentable {
    let url: URL

    func makeNSView(context: Context) -> WKWebView {
        return WKWebView()
    }

    func updateNSView(_ webView: WKWebView, context: Context) {
        let request = URLRequest(url: url)
        webView.load(request)
    }
}
```

### AppDelegate.swift
```swift
import Cocoa

class AppDelegate: NSObject, NSApplicationDelegate {
    var serverProcess: Process?

    func applicationDidFinishLaunching(_ notification: Notification) {
        startPythonServer()
    }

    func applicationWillTerminate(_ notification: Notification) {
        stopPythonServer()
    }

    func startPythonServer() {
        // Launch server.py as subprocess
    }

    func stopPythonServer() {
        serverProcess?.terminate()
    }
}
```

## User Experience

- **Launch**: Double-click app → Python server starts → WKWebView loads
- **Interface**: Clean minimal window, just the web app content
- **Controls**: Only macOS traffic lights (red/yellow/green) visible
- **Quit**: Close window or Cmd+Q → Server stops gracefully
- **No terminal**: All background, no visible console

## Notes

- **Models**: Download on first run (faster-whisper auto-downloads)
- **Updates**: Can implement auto-update via Sparkle framework
- **Code signing**: Required for distribution
- **Notarization**: Required for macOS 10.15+
- **Size**: App ~50MB (Swift app) + ~500MB (Python + models)
- **Microphone permission**: Info.plist needs NSMicrophoneUsageDescription
