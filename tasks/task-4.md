# Task 4: Universal Voice/Text Command Opener

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
- [ ] support multi commands: "would you open my whisper code base in vscode and start it in the web, telling me which tasks are left remaining to work"
- **Location:** New files in project root, integration with `server.py`

## Vision
A universal command system that accepts voice (via Whisper) or text input to execute common Mac workflows. Commands trigger zsh scripts, macros, or applications in new terminal windows. Includes LLM integration for natural language parsing and conversational command refinement.

## Core Features
1. **Input Methods**: Voice recording (using existing Whisper) or text entry
2. **Command Types**:
   - **Scripts**: `schedule`, `schedule today`, `schedule tomorrow` → Run custom zsh scripts
   - **Claude Integration**: `claude tell me what features we have` → Opens Claude Code with question
   - **Notes**: `note [content]` → Save timestamped notes from voice/text
3. **Execution Model**: Each command opens in new terminal window for visibility
4. **LLM Enhancement** (future): Parse natural language → valid command format, suggest options

## Architecture Considerations
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

## Example Workflows
```
User (voice): "schedule today"
→ Transcribe → Parse "schedule today" → Execute zsh script → New terminal window

User (text): "claude tell me what features we have to work in our whisper project"
→ Parse command → `cd /path/to/whisper && claude` → New terminal with context

User (voice): "note remember to update the API documentation tomorrow"
→ Transcribe → Save to notes/2025-10-28.md with timestamp
```

## Implementation Phases
1. **Phase 1**: Basic command parser + text input + terminal spawning
2. **Phase 2**: Voice integration using existing Whisper
3. **Phase 3**: Common commands (schedule, claude, note)
4. **Phase 4**: Command registry/config system
5. **Phase 5**: LLM integration for advanced parsing
6. **Phase 6**: Command history, favorites, and suggestions

## Technical Decisions Needed
- Command storage format (JSON, YAML, Python dict?)
- Note storage location and format (Markdown files? Database?)
- LLM provider for parsing (local model? API?)
- Command validation and safety checks
- Error handling for failed commands
