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

### Task 3: Change default port from 5000 to avoid macOS conflicts
- [x] Choose alternative port (5001, 8000, or 8080)
- [x] Update server.py with new port
- [x] Update run.sh browser launch URL
- [x] Update run.sh stop command to use new port
- [x] Check index.html for hardcoded port references
- [x] Update README.md with new port
- [x] Update CLAUDE.md with new port references
- [x] Test server on new port
- Location: `server.py`, `run.sh`, `index.html`, `README.md`, `CLAUDE.md`

**Problem:**
Port 5000 is commonly used by macOS system services (AirPlay Receiver/ControlCenter and WebKit Networking), causing conflicts when trying to run the Flask server.

**Design Considerations:**
1. **Port choice**: Common alternatives:
   - 5001: Next sequential, familiar
   - 8000: Common Python development port
   - 8080: Traditional HTTP alternate
2. **Backward compatibility**: Document the change clearly
3. **Configuration**: Consider if port should be configurable (environment variable)
4. **All references**: Ensure all hardcoded port references are updated
5. **User experience**: Update stop command to match new port

**Recommended Port:** 8000 (common Python convention, less likely to conflict)

### Task 4: Universal Voice/Text Command Opener
- [ ] Design command parser architecture (voice + text input)
- [ ] Create command registry system for mapping phrases to actions
- [ ] Implement voice input mode (record → transcribe → parse → execute)
- [ ] Implement text input mode (direct command entry)
- [ ] Add zshrc/macro integration layer
- [ ] Build command executor with new terminal window spawning
- [ ] Implement common commands:
  - [ ] `schedule [date]` - Opens scheduling script (defaults to today)
  - [ ] `claude [question/task]` - Opens Claude Code in project with context
  - [ ] `note [content]` - Save voice/text notes
- [ ] Add LLM integration for command parsing and validation
- [ ] Create interactive command confirmation/options dialog
- [ ] Build note-taking system with voice/text input
- [ ] Add command history and favorites
- [ ] Create configuration file for custom commands
- [ ] Add terminal window management (new windows per command)
- [ ] Test all command types (voice, text, scheduled, notes)
- Location: New files in project root, integration with `server.py`

**Vision:**
A universal command system that accepts voice (via Whisper) or text input to execute common Mac workflows. Commands trigger zsh scripts, macros, or applications in new terminal windows. Includes LLM integration for natural language parsing and conversational command refinement.

**Core Features:**
1. **Input Methods**: Voice recording (using existing Whisper) or text entry
2. **Command Types**:
   - **Scripts**: `schedule`, `schedule today`, `schedule tomorrow` → Run custom zsh scripts
   - **Claude Integration**: `claude tell me what features we have` → Opens Claude Code with question
   - **Notes**: `note [content]` → Save timestamped notes from voice/text
3. **Execution Model**: Each command opens in new terminal window for visibility
4. **LLM Enhancement** (future): Parse natural language → valid command format, suggest options

**Architecture Considerations:**
1. **Command Parser**:
   - Simple pattern matching initially (regex/keyword-based)
   - Extensible to LLM-based parsing later
   - Command registry/config file for easy additions
2. **Integration Points**:
   - Existing Whisper transcription for voice input
   - zshrc scripts and environment
   - macOS terminal automation (osascript/AppleScript)
   - Claude Code CLI integration
3. **Terminal Management**:
   - Spawn new Terminal.app windows per command
   - Pass context/parameters to each window
   - Keep command history across sessions
4. **Note System**:
   - Timestamped note storage
   - Voice or text input
   - Searchable/organized by date
5. **Future LLM Integration**:
   - Parse ambiguous commands into valid formats
   - Conversational command refinement
   - Context-aware suggestions
   - Learn user patterns/preferences

**Example Workflows:**
```
User (voice): "schedule today"
→ Transcribe → Parse "schedule today" → Execute zsh script → New terminal window

User (text): "claude tell me what features we have to work in our whisper project"
→ Parse command → `cd /path/to/whisper && claude` → New terminal with context

User (voice): "note remember to update the API documentation tomorrow"
→ Transcribe → Save to notes/2025-10-28.md with timestamp
```

**Implementation Phases:**
1. **Phase 1**: Basic command parser + text input + terminal spawning
2. **Phase 2**: Voice integration using existing Whisper
3. **Phase 3**: Common commands (schedule, claude, note)
4. **Phase 4**: Command registry/config system
5. **Phase 5**: LLM integration for advanced parsing
6. **Phase 6**: Command history, favorites, and suggestions

**Technical Decisions Needed:**
- Command storage format (JSON, YAML, Python dict?)
- Note storage location and format (Markdown files? Database?)
- LLM provider for parsing (local model? API?)
- Command validation and safety checks
- Error handling for failed commands
