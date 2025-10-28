# Task 2: Add command helpers to run.sh (start, setup, stop)

- [x] Design command structure and argument parsing
- [x] Implement `run.sh setup` - Create venv and install dependencies only
- [x] Implement `run.sh start` - Launch server (assumes setup is done)
- [x] Implement `run.sh stop` - Kill server on port 5000 with smart process detection
- [x] Add intelligent process detection to identify old server.py processes on port 5000
- [x] Add help/usage documentation
- [x] Test all commands in various scenarios
- **Location:** `run.sh`

## Implementation Summary
- Default behavior (no args): Shows help message
- `./run.sh start`: Sets up environment and launches server in new terminal
- `./run.sh setup`: Only creates venv and installs dependencies
- `./run.sh stop`: Intelligently detects and kills only server.py processes on port 5000
- Smart filtering: Ignores macOS system processes (like AirPlay/ControlCenter)
- Graceful shutdown: SIGTERM first, then SIGKILL if needed
- Updated README.md to use `./run.sh start` command

## Requirements
- `./run.sh` or `./run.sh start` - Full setup + launch (current behavior)
- `./run.sh setup` - Only create venv and install dependencies
- `./run.sh stop` - Kill any process using port 5000, specifically targeting server.py processes
- Smart detection: Identify and kill stale/old server.py processes on port 5000

## Design Considerations
1. **Backward compatibility**: Default behavior (no args) should match current functionality
2. **Process detection**: Use `lsof -ti:5000` to find PIDs, verify they're server.py processes
3. **Safe killing**: Graceful SIGTERM first, then SIGKILL if needed
4. **User feedback**: Clear messages about what's being killed and why
5. **Error handling**: Handle cases where no process is running, permission issues, etc.
