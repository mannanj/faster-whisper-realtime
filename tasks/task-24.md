# Task 24: Integration - File Upload to Playback Flow

- [ ] Test file upload from frontend to backend
- [ ] Verify SSE progress events stream correctly during processing
- [ ] Confirm progress bar updates with percentage and time estimates
- [ ] Verify audio segment files are created and stored correctly
- [ ] Confirm segment audio URLs are accessible from frontend
- [ ] Test HTML5 audio playback of served segments
- [ ] Verify transcriptions match their corresponding audio segments
- [ ] Test download functionality (TXT and JSON formats)
- [ ] Test status endpoint fallback when SSE connection drops
- [ ] Test session cleanup and file deletion after timeout
- [ ] Handle edge cases (corrupt files, unsupported formats, very long files)
- [ ] Test with the provided test-audio.mp3 file
- **Location:** Full stack integration

## Context

This task ensures the complete data flow works end-to-end:
1. Frontend uploads audio file via `/transcribe-file` POST request
2. Backend receives, splits into 5-min segments, and begins processing
3. Backend streams real-time progress via SSE:
   - Initial info (total segments, duration)
   - Progress updates (percent complete, time remaining)
   - Segment completions with transcription text
   - Final completion with session ID
4. Backend saves transcription files (TXT and JSON) upon completion
5. Frontend renders segments progressively as they complete
6. Frontend audio players load segments via `/audio-segment/<session_id>/<index>`
7. User can play each segment, read transcriptions, and download full transcript
8. Fallback: If connection drops, frontend polls `/transcribe-status/<session_id>`

## Data Flow Diagram (Updated with SSE)

```
Frontend                     Backend
   │                            │
   │──── POST /transcribe-file ─│
   │     (FormData: audio)      │
   │                            │
   │◄─── SSE: started ──────────│ Split into 5min segments
   │    {total_segments: 4}     │
   │                            │
   │◄─── SSE: progress ─────────│ Transcribing segment 0
   │    {percent: 0, eta: 300s} │
   │                            │
   │◄─── SSE: segment_complete ─│ Segment 0 done
   │    {transcription: "..."}  │
   │                            │
   │◄─── SSE: progress ─────────│ Transcribing segment 1
   │    {percent: 25, eta: 96s} │
   │                            │
   │◄─── SSE: segment_complete ─│ Segment 1 done
   │    {transcription: "..."}  │
   │                            │
   │        ... (repeat) ...    │
   │                            │
   │◄─── SSE: complete ─────────│ All done!
   │    {session_id: "123"}     │ Save transcription.txt
   │                            │ Save transcription.json
   │                            │
   │                            │
   │── GET /audio-segment/123/0 │
   │                            │
   │◄─── audio file (blob) ─────│
   │                            │
   │── GET /download-trans../123│
   │                            │
   │◄─── transcription.txt ─────│
   │                            │
   ▼                            ▼
Audio plays               Files served
Transcript shown
Download available
```

**Alternative: If connection drops**
```
Frontend                     Backend
   │                            │
   │  (connection lost)         │ Still processing...
   │                            │
   │── GET /transcribe-status   │
   │    /123                    │
   │◄─── {percent: 50, eta: 90}─│
   │                            │
   │  (poll every 5s)           │
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

- SSE events stream in real-time with accurate progress percentages
- Progress bar shows estimated time remaining
- Segments appear progressively as they complete (no waiting for all)
- Audio segments play smoothly without gaps
- Transcriptions are accurate and aligned with audio
- Download buttons work for both TXT and JSON formats
- Status endpoint returns accurate info if SSE connection drops
- No orphaned temp files after session ends
- Error handling displays user-friendly messages
- UI remains responsive during upload/processing
- Works reliably with 17+ minute files
