# Tasks

### Task 1: Fix run.sh edge case - Model download causing duplicate server start
- [x] Investigate why server appears to start twice during first-time model download
- [x] Identify the source of "Address already in use" error when model downloads
- [x] Determine if this is a terminal window issue or actual duplicate process
- [x] Design solution to prevent server conflicts during initial setup
- [x] Test solution with fresh venv and model download
- Location: `run.sh`, `server.py`

**Root Cause:**
Flask's debug mode with `debug=True` spawns two processes: a parent monitor and a child worker. Both processes load the Whisper model and attempt to bind to port 5000, causing "Address already in use" error.

**Solution Implemented:**
Added `use_reloader=False` to `app.run()` in server.py:60. This disables Flask's auto-reloader while maintaining debug mode features, ensuring only one server process starts.

**Problem Context:**
When running `run.sh` for the first time (with model download), the server appears to attempt starting twice in the same terminal window, causing "Address already in use" error on port 5000. The model download process seems to trigger this race condition.

**Design Considerations:**
1. **Process management**: Ensure only one server instance starts
2. **Model download blocking**: Make model download fully complete before server binds to port
3. **Terminal window timing**: Verify the "new terminal window" approach doesn't conflict during downloads
4. **Error handling**: Better detection of port conflicts with clear user guidance
5. **First-run experience**: Smooth model download without server startup issues

**Possible Solutions:**
- Add explicit wait/check after model download before starting server
- Move model download to separate initialization step
- Add port availability check before server.py execution
- Investigate if Flask auto-reload is causing duplicate start during model load
- Consider disabling debug mode during model download phase

### Task 2: Add command helpers to run.sh (start, setup, stop)
- [x] Design command structure and argument parsing
- [x] Implement `run.sh setup` - Create venv and install dependencies only
- [x] Implement `run.sh start` - Launch server (assumes setup is done)
- [x] Implement `run.sh stop` - Kill server on port 5000 with smart process detection
- [x] Add intelligent process detection to identify old server.py processes on port 5000
- [x] Add help/usage documentation
- [x] Test all commands in various scenarios
- Location: `run.sh`

**Implementation Summary:**
- Default behavior (no args): Shows help message
- `./run.sh start`: Sets up environment and launches server in new terminal
- `./run.sh setup`: Only creates venv and installs dependencies
- `./run.sh stop`: Intelligently detects and kills only server.py processes on port 5000
- Smart filtering: Ignores macOS system processes (like AirPlay/ControlCenter)
- Graceful shutdown: SIGTERM first, then SIGKILL if needed
- Updated README.md to use `./run.sh start` command

**Requirements:**
- `./run.sh` or `./run.sh start` - Full setup + launch (current behavior)
- `./run.sh setup` - Only create venv and install dependencies
- `./run.sh stop` - Kill any process using port 5000, specifically targeting server.py processes
- Smart detection: Identify and kill stale/old server.py processes on port 5000

**Design Considerations:**
1. **Backward compatibility**: Default behavior (no args) should match current functionality
2. **Process detection**: Use `lsof -ti:5000` to find PIDs, verify they're server.py processes
3. **Safe killing**: Graceful SIGTERM first, then SIGKILL if needed
4. **User feedback**: Clear messages about what's being killed and why
5. **Error handling**: Handle cases where no process is running, permission issues, etc.
