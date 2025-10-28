# Quick Start Guide - Mac App

## What You're Building

A **minimal, clean Mac app** that wraps your Flask web app with:
- ✨ **No browser bloat** - No address bar, tabs, or bookmarks
- 🪟 **Standard macOS window** - Just traffic lights (red/yellow/green buttons)
- ⚡ **Native performance** - Uses Safari's WebKit engine
- 🎯 **Automatic server** - Python backend starts/stops with app

## Visual Preview

```
┌─────────────────────────────────────┐
│ ● ● ●                               │  <- Only these controls visible
├─────────────────────────────────────┤
│                                     │
│   [Your Web App Interface Here]    │
│                                     │
│   - Clean                           │
│   - Minimal                         │
│   - Professional                    │
│                                     │
└─────────────────────────────────────┘
```

## Files Created

```
MacApp/
├── README.md                          # Full documentation
├── QUICKSTART.md                      # This file
├── setup-xcode.sh                     # Setup helper script
└── FasterWhisperRealtime/
    ├── FasterWhisperRealtimeApp.swift # Main app entry
    ├── AppDelegate.swift              # Server management
    ├── ContentView.swift              # WebView wrapper
    └── Info.plist                     # App configuration
```

## Setup (5 minutes)

### Option A: Automated Helper

```bash
cd MacApp
./setup-xcode.sh
```

Then follow the printed instructions.

### Option B: Manual Setup

1. **Open Xcode**

2. **Create New Project**
   - File → New → Project
   - macOS → App
   - Product Name: `FasterWhisperRealtime`
   - Interface: `SwiftUI`
   - Language: `Swift`

3. **Add Swift Files**
   - Delete Xcode's default Swift files
   - Drag all `.swift` files from `FasterWhisperRealtime/` into project
   - Check "Copy items if needed"

4. **Add Backend Files to Resources**
   - Select project in sidebar
   - Select target → Build Phases tab
   - Copy Bundle Resources section
   - Click `+` and add:
     - `../server.py`
     - `../index.html`
     - `../requirements.txt`

5. **Build and Run**
   - Press `⌘R`
   - App launches with embedded web interface!

## What Happens When You Run

1. ⚙️  App launches
2. 🐍 Python server starts in background
3. ⏳ App polls server until ready
4. 🌐 WKWebView loads localhost:10000
5. ✅ You see your web app in a clean native window!

## Customization

### Change Window Size

Edit `FasterWhisperRealtimeApp.swift:13`:
```swift
.frame(minWidth: 900, minHeight: 700)  // Change these values
```

### Change Server Port

Edit both:
- `server.py`: Change port in `app.run()`
- `ContentView.swift:15`: Change `"http://localhost:10000"`

### Add App Icon

1. Create `.icns` file (use Image2Icon app)
2. Add to Xcode: Assets.xcassets → AppIcon

## Troubleshooting

### "Server not starting"
- Check Python 3 is installed: `python3 --version`
- Install dependencies: `pip3 install -r requirements.txt`

### "Port already in use"
- Stop existing server: `./run.sh stop`
- Or change port in both files (see Customization)

### "Black screen on launch"
- Server is still starting, wait 2-3 seconds
- Check Xcode console for server logs

## Next Steps

- **Add app icon** for professional look
- **Code sign** for distribution (Xcode → Signing & Capabilities)
- **Bundle Python** for standalone distribution (see README.md)
- **Create DMG** for easy sharing

## Technical Details

- **Framework**: SwiftUI + WKWebView
- **Backend**: Python 3 + Flask + faster-whisper
- **Server management**: Process API with health monitoring
- **Window style**: Hidden title bar with visible traffic lights
- **Loading state**: Automatic retry with progress indicator

---

**Need help?** See full documentation in `README.md`

**Ready to build?** Run `./setup-xcode.sh` or follow manual steps above!
