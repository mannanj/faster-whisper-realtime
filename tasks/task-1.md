# Task 1: Fix run.sh edge case - Model download causing duplicate server start

- [x] Investigate why server appears to start twice during first-time model download
- [x] Identify the source of "Address already in use" error when model downloads
- [x] Determine if this is a terminal window issue or actual duplicate process
- [x] Design solution to prevent server conflicts during initial setup
- [x] Test solution with fresh venv and model download
- **Location:** `run.sh`, `server.py`

## Root Cause
Flask's debug mode with `debug=True` spawns two processes: a parent monitor and a child worker. Both processes load the Whisper model and attempt to bind to port 5000, causing "Address already in use" error.

## Solution Implemented
Added `use_reloader=False` to `app.run()` in server.py:60. This disables Flask's auto-reloader while maintaining debug mode features, ensuring only one server process starts.

## Problem Context
When running `run.sh` for the first time (with model download), the server appears to attempt starting twice in the same terminal window, causing "Address already in use" error on port 5000. The model download process seems to trigger this race condition.

## Design Considerations
1. **Process management**: Ensure only one server instance starts
2. **Model download blocking**: Make model download fully complete before server binds to port
3. **Terminal window timing**: Verify the "new terminal window" approach doesn't conflict during downloads
4. **Error handling**: Better detection of port conflicts with clear user guidance
5. **First-run experience**: Smooth model download without server startup issues

## Possible Solutions
- Add explicit wait/check after model download before starting server
- Move model download to separate initialization step
- Add port availability check before server.py execution
- Investigate if Flask auto-reload is causing duplicate start during model load
- Consider disabling debug mode during model download phase
