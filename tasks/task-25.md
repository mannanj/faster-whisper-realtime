# Task 25: Enhance transcribe-file Endpoint for Long Audio Files

- [x] Add streaming progress updates via SSE (Server-Sent Events)
- [x] Create status endpoint to check transcription progress
- [x] Save transcription results to files (JSON and TXT)
- [x] Add download endpoint for saved transcription files
- [x] Improve error recovery with progress persistence
- [x] Add estimated time remaining calculation
- [x] Test with 17-minute audio file
- **Location:** `server.py`

## Context

Current `/transcribe-file` endpoint processes long audio files (17+ minutes) but has limitations:
- No progress updates during processing (blind waiting)
- No way to check status if request times out
- Results only returned as JSON response (lost if connection drops)
- No file output for transcription

## Design

### 1. Status Tracking System
Store processing state in session directory:
```json
{
  "status": "processing",
  "current_segment": 2,
  "total_segments": 4,
  "percent_complete": 50,
  "estimated_seconds_remaining": 90,
  "started_at": 1234567890
}
```

### 2. New Endpoints
- `POST /transcribe-file` - Now uses SSE for progress streaming
- `GET /transcribe-status/<session_id>` - Check current status
- `GET /download-transcription/<session_id>` - Download final transcription
- `GET /download-transcription/<session_id>/json` - Download JSON format

### 3. File Outputs
Save to `SESSIONS_DIR/<session_id>/`:
- `transcription.txt` - Plain text full transcription
- `transcription.json` - Structured data with segments
- `status.json` - Current processing status

### 4. Progress Updates via SSE
```javascript
{type: 'started', total_segments: 4, total_duration: 1020}
{type: 'progress', segment: 0, percent: 25, estimated_remaining: 180}
{type: 'segment_complete', segment: 0, transcription: "..."}
{type: 'complete', session_id: "abc-123"}
```

## Time Estimates (17-min file with base model)
- Total segments: ~4 (3×5min + 1×2min)
- Time per segment: 30-90s
- Total processing: 2-5 minutes
- RTF: ~0.15-0.30x

## Success Criteria
- User sees real-time progress updates
- Transcription survives connection interruptions
- Final files downloadable from session
- Status queryable at any time
- Works reliably with 17+ minute files
