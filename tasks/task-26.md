# Task 26: Add Word-Level Timestamps Support

- [x] Update backend to accept `word_timestamps` parameter in `/transcribe-file` endpoint
- [x] Modify transcription logic to request word-level timestamps from faster-whisper
- [x] Update JSON output format to include word-level timestamp data
- [x] Update frontend File Upload tab to request word timestamps
- [x] Test with sample audio file to verify word timestamps are returned
- **Location:** `server.py`, `index.html`

## Context

Currently, the transcription output only includes segment-level timestamps (start_time, end_time for each segment). Users want word-level timestamps that show the exact timing for each individual word in the transcription.

The faster-whisper library supports word-level timestamps through the `word_timestamps=True` parameter in the `model.transcribe()` method.

## Design

### 1. Backend Changes (server.py)

Update the `/transcribe-file` endpoint to:
- Accept optional `word_timestamps` parameter (default: false)
- Pass `word_timestamps=True` to `model.transcribe()` when requested
- Extract word-level timestamp data from segments
- Include word data in the transcription JSON output

**Example transcribe call with word timestamps:**
```python
segments, info = model.transcribe(
    str(segment_path),
    beam_size=1,
    vad_filter=True,
    word_timestamps=True  # Enable word-level timestamps
)
```

**Updated JSON structure:**
```json
{
  "total_duration": 1092.15,
  "full_transcription": "Hi guys...",
  "segments": [
    {
      "index": 0,
      "start_time": 0.0,
      "end_time": 300.0,
      "transcription": "Hi guys, where is...",
      "audio_url": "/audio-segment/...",
      "language": "en",
      "words": [
        {"word": "Hi", "start": 0.0, "end": 0.2, "probability": 0.99},
        {"word": "guys", "start": 0.2, "end": 0.5, "probability": 0.98},
        ...
      ]
    }
  ]
}
```

### 2. Frontend Changes (index.html)

Update the File Upload tab to:
- Always request word timestamps for file uploads (set `word_timestamps=true`)
- No UI changes needed initially (just collect the data)

**FormData update:**
```javascript
formData.append('word_timestamps', 'true');
```

### 3. Real-time Tab

For now, keep the real-time transcription WITHOUT word timestamps to maintain speed. Word timestamps can be added later if needed.

## Performance Considerations

- Word-level timestamps may slightly increase processing time
- The increase should be minimal (< 10% overhead)
- File size of JSON output will increase due to additional word data

## Success Criteria

- File uploads include word-level timestamp data in JSON output
- Each word has accurate start/end times and probability scores
- Existing functionality remains unchanged
- Data is stored in session directory for later retrieval
