# Task 23: Frontend - File Upload Tab with Segmented Playback

- [ ] Add tab navigation UI (Real-time / File Upload tabs)
- [ ] Create file upload interface with drag-and-drop support
- [ ] Build segmented view displaying 5-minute chunks
- [ ] Add audio player for each segment (HTML5 audio element)
- [ ] Display transcription text alongside each audio segment
- [ ] Show upload progress indicator
- [ ] Add copy functionality for individual segments and full transcript
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
- Use tabs that toggle visibility of content divs
- File upload via FormData and fetch API
- Display segments progressively as they're transcribed
- Audio elements load segment URLs from server
- Maintain gradient color scheme and curved borders
- Use same font (Geist) and styling as real-time page
