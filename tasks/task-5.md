# Task 5: Real-Time Streaming Transcription (SSE)

- [x] Modify `/transcribe` endpoint to use Server-Sent Events (SSE)
- [x] Stream segments as they're transcribed using `flask.stream_with_context`
- [x] Send each segment as JSON event with timestamp and text
- [x] Add segment timing metadata to each event
- [x] Handle completion event to signal transcription finished
- **Location:** `server.py`

## Purpose
Enable real-time streaming of transcription segments so users see text appear progressively as the model processes audio, rather than waiting for complete transcription.

## Technical Approach

### Backend Changes (server.py)
Use Server-Sent Events (SSE) with `text/event-stream` content type. The faster-whisper model already returns an iterator of segments, which is perfect for streaming.

**SSE Response Format:**
```python
def generate_segments(audio_path):
    segments, info = model.transcribe(audio_path, beam_size=5)

    # Send metadata first
    yield f"data: {json.dumps({'type': 'metadata', 'language': info.language, 'duration': info.duration})}\n\n"

    # Stream each segment
    for segment in segments:
        yield f"data: {json.dumps({'type': 'segment', 'start': segment.start, 'end': segment.end, 'text': segment.text})}\n\n"

    # Send completion event
    yield f"data: {json.dumps({'type': 'complete'})}\n\n"

@app.route('/transcribe', methods=['POST'])
def transcribe():
    # Save audio to temp file
    # Return Response(generate_segments(temp_path), mimetype='text/event-stream')
```

### Key Implementation Details
1. Keep temporary file cleanup until stream completes
2. Use `Response(stream_with_context(...), mimetype='text/event-stream')`
3. Include error handling with error event type
4. Maintain backwards compatibility or create new endpoint `/transcribe-stream`

## Event Types
- `metadata`: Language detection and duration info
- `segment`: Individual transcription segment with timestamps
- `complete`: Signals end of transcription
- `error`: Error information if transcription fails

## Benefits
- Users see immediate progress during transcription
- Better UX for longer audio files
- Leverages existing faster-whisper segment iterator
- Simple implementation with minimal dependencies

## Testing
- Test with short audio (< 5 seconds)
- Test with medium audio (30-60 seconds)
- Test with long audio (2+ minutes)
- Verify error handling if audio processing fails
