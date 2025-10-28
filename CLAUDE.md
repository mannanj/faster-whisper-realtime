# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Task Workflow

**1. Create task in `tasks.md`:**
```markdown
### Task N: Task Title
- [ ] Subtask 1
- [ ] Subtask 2
- Location: `path/to/files`
```

**2. Before starting, verify work isn't already done:**
- Check codebase for task's changes
- Review files in Location field
- If complete but unmarked:
  - Mark subtasks `[x]` in tasks.md
  - Commit with `[Task-N]` tag
  - Push and skip to next task

**3. Complete subtasks, mark `[x]` in tasks.md**

**4. Commit:**
```bash
git add .
git commit -m "Task N: Task Title

- [x] Subtask 1
- [x] Subtask 2
- Location: \`path/to/files\`

[Task-N]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Requirements:**
- Complete task entry in commit message
- All subtasks with status
- `[Task-N]` tag for tracking
- One task per commit

**5. Push:** `git push`

## Development Commands

### Quick Start
```bash
# One-command setup and launch (recommended)
./run.sh
```

This script:
- Creates Python virtual environment (if needed)
- Installs/updates all dependencies
- Launches Flask server in new terminal window
- Opens browser automatically at http://localhost:10000

### Manual Commands (if not using run.sh)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Flask server (port 10000)
python3 server.py
```

## Architecture

### Application Structure
Simple full-stack real-time speech transcription application with Flask backend and vanilla JavaScript frontend served as static files.

**Data Flow**: Browser MediaRecorder API → Audio blob (WebM) → Flask POST /transcribe → faster-whisper model → Transcription JSON response → DOM update

### Backend (server.py)
- **Framework**: Flask with CORS enabled for local development
- **ML Model**: faster-whisper (CTranslate2-optimized Whisper implementation)
- **Default Model**: `base` for speed/accuracy balance
- **Model Options**: tiny, base, small, medium, large-v2, large-v3 (configurable at server.py:14)
- **Endpoints**:
  - `GET /` - Serves index.html
  - `POST /transcribe` - Accepts audio file, returns transcription JSON
- **Audio Handling**: Temporary file storage for audio processing, automatic cleanup
- **Response Format**:
  ```json
  {
    "transcription": "text",
    "language": "en",
    "duration": 5.2
  }
  ```

### Frontend (index.html)
- **Architecture**: Single-page application with vanilla JavaScript
- **Styling**: Embedded CSS with gradient design system
- **Audio Capture**: Browser MediaRecorder API (WebM format)
- **UI State Management**: Pure JavaScript DOM manipulation
- **Key Features**:
  - Real-time recording status indicators
  - Animated recording button with pulse effect
  - Automatic language detection display
  - Recording duration tracking
  - Copy-to-clipboard functionality

### Key Dependencies
- **faster-whisper**: ML model for speech-to-text transcription
- **flask**: Web server framework
- **flask-cors**: CORS middleware for development
- **requests**: HTTP library (utility dependency)

### Development Notes
- Server runs on port 10000 by default
- First run downloads Whisper model (~150MB for base model)
- Model loaded at server startup, not per-request
- Audio temporarily saved as .webm files during transcription
- Frontend expects backend on localhost:10000 (same origin)
- Browser must support MediaRecorder API (Chrome, Firefox, Safari, Edge)

## Code Standards

### Simplicity First
- **Minimal dependencies**: Prefer vanilla JavaScript over frameworks when possible
- **Single-file components**: Keep HTML/CSS/JS together for simple features
- **No build process**: Direct browser compatibility without transpilation
- **Clear data flow**: Request → Process → Response pattern

### Comment Policy
- **Minimize comments**: Only include comments that explain non-obvious technical decisions or provide critical context
- **Remove obvious comments**: Do not comment code that is self-explanatory
- **Preserve critical context**: Keep comments that explain "why" rather than "what"
- Examples of acceptable comments:
  - Model configuration trade-offs (server.py:11-12)
  - API limitations or browser compatibility notes
  - Temporary file handling reasoning
  - Audio format requirements
- Examples of comments to remove:
  - "Save audio file" (obvious)
  - "Return JSON response" (obvious)
  - "Add click listener" (obvious)

### Python Standards
- **Type hints**: Use where they improve clarity
- **Error handling**: Always handle model transcription failures
- **Resource cleanup**: Ensure temporary files are deleted
- **Flask patterns**: Use standard Flask decorators and response formats

### Frontend Standards
- **Progressive enhancement**: Core functionality works without JavaScript features
- **Responsive design**: Mobile-friendly layouts
- **User feedback**: Clear status messages for all operations
- **Error handling**: Graceful degradation when APIs fail
