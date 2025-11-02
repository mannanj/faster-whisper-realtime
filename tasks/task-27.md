# Task 27: Display Past Upload History in Frontend

- [x] Add backend endpoint to list all available sessions
- [x] Create new "History" tab in frontend
- [x] Display list of past uploads with metadata (date, duration, status)
- [x] Add "View" button to load transcription from past session
- [x] Add "Download" buttons for TXT and JSON formats
- [x] Add "Delete" button to remove old sessions
- [x] Handle session cleanup (auto-delete after expiry)
- **Location:** `server.py`, `index.html`

## Context

Currently, users can upload and transcribe files, but there's no way to view past transcriptions after leaving the page. The backend already stores sessions in `SESSIONS_DIR`, but the frontend has no interface to browse and access them.

## Design

### 1. Backend Endpoints (server.py)

Add new endpoints:

**GET /sessions**
- List all available sessions with metadata
- Return array of session objects sorted by date (newest first)

```json
[
  {
    "session_id": "e1a05747-6245-4f94-b57f-b4513e4d1d97",
    "status": "complete",
    "total_duration": 1092.15,
    "total_segments": 4,
    "created_at": 1762062803.56,
    "completed_at": 1762062803.56
  }
]
```

**GET /session/<session_id>**
- Return full transcription data for a specific session
- Read and return the `transcription.json` file

**DELETE /session/<session_id>**
- Delete a specific session directory
- Return success/error status

### 2. Frontend - New "History" Tab (index.html)

Add a third tab "History" alongside "Real-time" and "File Upload":

```html
<div class="tabs">
    <div class="tab active" data-tab="realtime">Real-time</div>
    <div class="tab" data-tab="upload">File Upload</div>
    <div class="tab" data-tab="history">History</div>
</div>
```

**History Tab UI:**
- Auto-refresh session list when tab is opened
- Show empty state when no sessions exist
- Display sessions as cards with:
  - Date/time of upload
  - Duration
  - Status (complete/processing/error)
  - Preview of first ~100 characters
- Action buttons for each session:
  - "View" - Load and display full transcription
  - "Download TXT" - Download text file
  - "Download JSON" - Download JSON file
  - "Delete" - Remove session

**Example session card:**
```
┌─────────────────────────────────────────┐
│ Nov 2, 2025 - 1:48 AM                   │
│ Duration: 18:12                         │
│ Status: Complete                        │
│                                         │
│ "Hi guys, where is the devor bling..."  │
│                                         │
│ [View] [Download TXT] [JSON] [Delete]  │
└─────────────────────────────────────────┘
```

### 3. Session Viewer

When user clicks "View" on a session:
- Load full transcription data
- Display in a modal or expand the card
- Show segments with playback controls (reuse existing segment player component)
- Allow copying text
- Show word-level timestamps if available (from Task 26)

### 4. Auto-cleanup

Current `SESSION_TIMEOUT` is 3600 seconds (1 hour). Consider:
- Increasing timeout to 24-48 hours for better user experience
- Adding manual cleanup button "Delete All Old Sessions"
- Showing session age/expiry time

## Technical Notes

- Use existing session directory structure
- Leverage existing download endpoints (`/download-transcription/<session_id>`)
- Fetch sessions on History tab load
- Format timestamps with JavaScript `Date` object
- Handle missing/corrupted sessions gracefully

## Success Criteria

- Users can see list of all past uploads
- Users can view full transcription from any session
- Users can download transcripts in TXT/JSON format
- Users can delete individual sessions
- Empty state shown when no sessions exist
- Session list refreshes when new upload completes
