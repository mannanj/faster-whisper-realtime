# Task 24: Integration - File Upload to Playback Flow

- [ ] Test file upload from frontend to backend
- [ ] Verify audio segment files are created and stored correctly
- [ ] Confirm segment audio URLs are accessible from frontend
- [ ] Test HTML5 audio playback of served segments
- [ ] Verify transcriptions match their corresponding audio segments
- [ ] Test session cleanup and file deletion after timeout
- [ ] Handle edge cases (corrupt files, unsupported formats, very long files)
- [ ] Test with the provided test-audio.mp3 file
- **Location:** Full stack integration

## Context

This task ensures the complete data flow works end-to-end:
1. Frontend uploads audio file via `/transcribe-file`
2. Backend receives, splits, transcribes, and stores segments
3. Backend returns JSON with segment metadata and audio URLs
4. Frontend renders segments with transcription text
5. Frontend audio players load and play segments via `/audio-segment/<session_id>/<index>`
6. User can play each segment and read its transcription side-by-side

## Data Flow Diagram

```
Frontend                     Backend
   │                            │
   │──── POST /transcribe-file ─│
   │     (FormData: audio)      │
   │                            │
   │                         Split into
   │                         5min segments
   │                            │
   │                         Transcribe
   │                         each segment
   │                            │
   │                         Store segments
   │                         /tmp/sessions/
   │                         session_123/
   │                            │
   │─── JSON response ──────────│
   │    {segments: [            │
   │      {audio_url: "/audio-  │
   │       segment/123/0"}]}    │
   │                            │
   │                            │
   │── GET /audio-segment/123/0 │
   │                            │
   │─── audio file (blob) ──────│
   │                            │
   ▼                            ▼
Audio plays               File served
Transcript shown
```

## Test Cases

1. **Small file (< 5 minutes):** Should create 1 segment, play correctly
2. **Medium file (10-15 minutes):** Should create 2-3 segments
3. **Large file (30+ minutes):** Should create 6+ segments, test performance
4. **test-audio.mp3:** User's specific file
5. **Different formats:** MP3, WAV, M4A
6. **Corrupt file:** Should show error message
7. **Concurrent uploads:** Multiple users shouldn't interfere

## Success Criteria

- Audio segments play smoothly without gaps
- Transcriptions are accurate and aligned with audio
- No orphaned temp files after session ends
- Error handling displays user-friendly messages
- UI remains responsive during upload/processing
