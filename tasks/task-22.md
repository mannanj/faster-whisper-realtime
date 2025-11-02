# Task 22: Backend - File Upload with Audio Segmentation

- [x] Create `/transcribe-file` POST endpoint to accept audio file uploads (any format)
- [x] Implement audio file splitting into 5-minute segments using pydub/ffmpeg
- [x] Process each segment with faster-whisper and return segment metadata
- [x] Store temporary audio segments on server in session-specific directories
- [x] Create `/audio-segment/<session_id>/<index>` GET endpoint to serve segment audio files
- [x] Return JSON response with transcriptions and segment file paths
- [x] Add cleanup mechanism for temporary segment files (session timeout)
- [x] Handle various audio formats (mp3, wav, m4a, webm)
- **Location:** `server.py`, `requirements.txt`

## Context

Create a new endpoint that handles longer audio files by:
1. Accepting uploaded audio file (any common format)
2. Converting to standardized format if needed
3. Splitting into 5-minute segments
4. Transcribing each segment individually
5. Returning:
   - Segment transcriptions with timestamps
   - URLs to access each audio segment for playback
   - Total duration and segment count

## Technical Notes

- Use pydub for audio splitting (add to requirements.txt)
- Store segments in temp directory with unique session ID
- Each segment should be accessible via `/audio-segment/<session_id>/<segment_index>` endpoint
- Response format:
```json
{
  "session_id": "unique_id",
  "total_duration": 1800.0,
  "segments": [
    {
      "index": 0,
      "start_time": 0.0,
      "end_time": 300.0,
      "transcription": "text here",
      "audio_url": "/audio-segment/session_id/0",
      "language": "en"
    }
  ]
}
```

## Dependencies to Add
- pydub (for audio manipulation)
- ffmpeg system dependency (document in README)
