# Task 23: Frontend - File Upload Tab with Segmented Playback

- [ ] Add tab navigation UI (Real-time / File Upload tabs)
- [ ] Create file upload interface with drag-and-drop support
- [ ] Implement SSE event listener for real-time progress updates
- [ ] Display progress bar with percentage and estimated time remaining
- [ ] Build segmented view displaying 5-minute chunks as they complete
- [ ] Add audio player for each segment (HTML5 audio element)
- [ ] Display transcription text alongside each audio segment
- [ ] Add download buttons for full transcription (TXT and JSON formats)
- [ ] Add copy functionality for individual segments and full transcript
- [ ] Handle connection interruptions with status endpoint fallback
- [ ] Match existing design system (colors, fonts, borders)
- **Location:** `index.html` (or new `upload.html` if separate)

## Context

Add a second tab to the application that allows users to:
1. Upload audio files of any length
2. View the file split into 5-minute segments
3. Play each segment's audio
4. Read the transcription for each segment
5. Copy transcriptions (individual or all)

## UI Design

```
┌─────────────────────────────────────┐
│  [Real-time] [File Upload]          │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Drop file or click to      │   │
│  │  upload                      │   │
│  └─────────────────────────────┘   │
│                                     │
│  After upload:                      │
│                                     │
│  Segment 1 (0:00 - 5:00)            │
│  ┌─────────────────────────────┐   │
│  │ [▶] ━━━━━━━━━━━━━━━ 5:00   │   │
│  └─────────────────────────────┘   │
│  Transcription text here...         │
│  [Copy]                             │
│                                     │
│  Segment 2 (5:00 - 10:00)           │
│  ┌─────────────────────────────┐   │
│  │ [▶] ━━━━━━━━━━━━━━━ 5:00   │   │
│  └─────────────────────────────┘   │
│  Transcription text here...         │
│  [Copy]                             │
│                                     │
│  [Copy All Transcriptions]          │
└─────────────────────────────────────┘
```

## Key Features
- Tab switching preserves state
- Progress indicator during upload/processing
- Each segment shows:
  - Time range (e.g., "0:00 - 5:00")
  - Playable audio with standard controls
  - Full transcription text
  - Individual copy button
- Visual separation between segments
- Responsive design matching current app style

## Technical Notes

### SSE Progress Streaming (Updated)
Backend now uses Server-Sent Events (SSE) for real-time progress updates:

**Event Types to Handle:**
```javascript
// 1. started - Initial info
{type: 'started', session_id: '...', total_segments: 4, total_duration: 1092}

// 2. progress - Progress updates
{type: 'progress', segment: 0, total_segments: 4, percent: 0, estimated_remaining: 300}

// 3. segment_complete - Each segment result
{type: 'segment_complete', segment: 0, transcription: "...", start_time: 0, end_time: 300}

// 4. complete - Final result
{type: 'complete', session_id: '...', total_duration: 1092, segments: [...]}

// 5. error - Error handling
{type: 'error', message: '...'}
```

**Simple Implementation:**
```javascript
const formData = new FormData();
formData.append('audio', fileInput.files[0]);

fetch('/transcribe-file', {method: 'POST', body: formData})
  .then(response => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    function processStream() {
      reader.read().then(({done, value}) => {
        if (done) return;

        const text = decoder.decode(value);
        const lines = text.split('\n');

        lines.forEach(line => {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            handleEvent(data); // Update UI based on data.type
          }
        });

        processStream();
      });
    }
    processStream();
  });
```

### Fallback for Disconnections
If connection drops, poll status endpoint:
```javascript
setInterval(() => {
  fetch(`/transcribe-status/${sessionId}`)
    .then(r => r.json())
    .then(status => updateProgress(status.percent_complete));
}, 5000);
```

### Download Functionality
- Text: `GET /download-transcription/<session_id>`
- JSON: `GET /download-transcription/<session_id>/json`

### UI Implementation
- Use tabs that toggle visibility of content divs
- File upload via FormData and fetch API
- Display segments progressively as SSE events arrive
- Audio elements load segment URLs from server: `/audio-segment/<session_id>/<index>`
- Maintain gradient color scheme and curved borders
- Use same font (Geist) and styling as real-time page
- Show spinner/progress bar during processing
- Display estimated time remaining during transcription
