# Task 12: Continuous Real-Time Streaming Transcription

- [x] Modify MediaRecorder to use timeslice for continuous chunk generation
- [x] Send audio chunks to server while recording (not after stop)
- [x] Create new `/transcribe-live` endpoint for streaming audio input
- [x] Implement WebSocket or chunked POST for bidirectional streaming
- [x] Display transcription text as it arrives during active recording
- [x] Handle overlapping/continuous audio context between chunks
- [x] Add visual indicator showing live transcription status
- [x] Implement proper cleanup when recording stops
- **Location:** `server.py`, `index.html`

## Purpose
Enable true real-time transcription where text appears on screen while the user is still speaking, rather than waiting for recording to stop. Audio is sent to the server in chunks as it's recorded, and transcription results stream back immediately.

## Current Behavior vs. Target

**Current (Task 5):**
1. User clicks "Start Recording"
2. Audio records locally
3. User clicks "Stop Recording"
4. Audio blob sent to server
5. Transcription streams back via SSE
6. Text appears progressively

**Target (Task 12):**
1. User clicks "Start Recording"
2. Audio chunks sent to server **every 2-3 seconds while recording**
3. Server transcribes each chunk immediately
4. Text appears on screen **while still recording**
5. User sees their words appear in near real-time
6. User clicks "Stop Recording" to finish

## Technical Approach

### Frontend Changes (index.html)

#### 1. MediaRecorder with timeslice

```javascript
// Start recording with timeslice to generate chunks
mediaRecorder = new MediaRecorder(stream);
mediaRecorder.start(2000); // Generate chunk every 2 seconds

mediaRecorder.addEventListener('dataavailable', async (event) => {
  if (event.data.size > 0) {
    // Send chunk to server immediately
    await sendChunkForTranscription(event.data);
  }
});
```

#### 2. Send Chunks While Recording

**Option A: Sequential POST requests**
```javascript
async function sendChunkForTranscription(audioBlob) {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'chunk.webm');
  formData.append('chunk_index', chunkCounter++);
  formData.append('session_id', sessionId);

  const response = await fetch('/transcribe-live', {
    method: 'POST',
    body: formData
  });

  // Read SSE stream for this chunk
  const reader = response.body.getReader();
  // ... (same SSE parsing as Task 5)
}
```

**Option B: WebSocket (more efficient for true streaming)**
```javascript
const ws = new WebSocket('ws://localhost:10000/transcribe-live');

ws.onopen = () => {
  console.log('WebSocket connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'segment') {
    // Append transcription text in real-time
    transcription.textContent += data.text;
  }
};

// Send audio chunks via WebSocket
mediaRecorder.addEventListener('dataavailable', async (event) => {
  if (event.data.size > 0 && ws.readyState === WebSocket.OPEN) {
    // Convert blob to ArrayBuffer and send
    const arrayBuffer = await event.data.arrayBuffer();
    ws.send(arrayBuffer);
  }
});
```

### Backend Changes (server.py)

#### Option A: POST-based approach

```python
@app.route('/transcribe-live', methods=['POST'])
def transcribe_live():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio chunk provided'}), 400

    audio_chunk = request.files['audio']
    chunk_index = request.form.get('chunk_index', 0)
    session_id = request.form.get('session_id', 'default')

    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
        audio_chunk.save(temp_audio.name)
        temp_path = temp_audio.name

    def generate_segments():
        try:
            segments, info = model.transcribe(temp_path, beam_size=5)

            # Only send metadata on first chunk
            if int(chunk_index) == 0:
                yield f"data: {json.dumps({'type': 'metadata', 'language': info.language})}\n\n"

            for segment in segments:
                yield f"data: {json.dumps({'type': 'segment', 'start': segment.start, 'end': segment.end, 'text': segment.text})}\n\n"

            yield f"data: {json.dumps({'type': 'chunk_complete', 'chunk_index': chunk_index})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    return Response(stream_with_context(generate_segments()), mimetype='text/event-stream')
```

#### Option B: WebSocket approach (recommended for lower latency)

```python
from flask_sock import Sock

sock = Sock(app)

@sock.route('/transcribe-live')
def transcribe_live_ws(ws):
    """WebSocket endpoint for real-time audio streaming."""
    chunk_counter = 0

    while True:
        # Receive audio chunk
        audio_data = ws.receive()

        if audio_data is None:
            break

        # Save chunk to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
            temp_audio.write(audio_data)
            temp_path = temp_audio.name

        try:
            # Transcribe chunk
            segments, info = model.transcribe(temp_path, beam_size=5)

            # Send metadata on first chunk
            if chunk_counter == 0:
                ws.send(json.dumps({
                    'type': 'metadata',
                    'language': info.language,
                    'duration': info.duration
                }))

            # Send each segment
            for segment in segments:
                ws.send(json.dumps({
                    'type': 'segment',
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text
                }))

            # Send chunk complete
            ws.send(json.dumps({
                'type': 'chunk_complete',
                'chunk_index': chunk_counter
            }))

            chunk_counter += 1

        except Exception as e:
            ws.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
```

## Key Challenges & Solutions

### 1. Audio Context Continuity

**Problem:** Each chunk is transcribed independently, may miss words at boundaries.

**Solution A:** Overlapping chunks
```javascript
// Keep last 500ms of previous chunk and prepend to next chunk
let previousChunkTail = null;

mediaRecorder.addEventListener('dataavailable', async (event) => {
  let chunkToSend = event.data;

  if (previousChunkTail) {
    // Merge previous tail with new chunk
    chunkToSend = new Blob([previousChunkTail, event.data]);
  }

  // Extract last 500ms for next chunk
  previousChunkTail = await extractTail(event.data, 500);

  await sendChunkForTranscription(chunkToSend);
});
```

**Solution B:** Longer chunks (3-5 seconds)
- Reduces boundary issues
- Acceptable latency for most use cases

### 2. Duplicate/Overlapping Text

**Problem:** Overlapping chunks may produce duplicate transcriptions.

**Solution:** Deduplicate on frontend
```javascript
let lastSegmentText = '';

function appendSegment(text) {
  // Check if this segment overlaps with previous
  if (text.startsWith(lastSegmentText.slice(-20))) {
    // Skip duplicate
    return;
  }

  transcription.textContent += ' ' + text;
  lastSegmentText = text;
}
```

### 3. Transcription Latency

**Problem:** faster-whisper takes ~1-2 seconds per chunk.

**Solution:**
- Use `tiny` or `base` model for lower latency
- Chunk size 2-3 seconds balances latency vs. accuracy
- Consider model quantization for faster inference

### 4. Network Buffering

**Problem:** Network delays can cause out-of-order chunks.

**Solution:** Include chunk sequence numbers
```javascript
formData.append('chunk_index', chunkCounter++);
formData.append('session_id', sessionId);
```

Backend reorders if needed.

## UI/UX Enhancements

### Live Transcription Indicator

```html
<div class="live-indicator">
  <span class="pulse-dot"></span>
  <span>Live Transcription</span>
</div>
```

```css
.live-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #f5576c;
}

.pulse-dot {
  width: 10px;
  height: 10px;
  background: #f5576c;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}
```

### Progressive Text Display

```javascript
// Append text smoothly with typing effect (optional)
function appendText(text) {
  const words = text.split(' ');
  words.forEach((word, i) => {
    setTimeout(() => {
      transcription.textContent += word + ' ';
    }, i * 50); // 50ms delay per word
  });
}
```

## Dependencies

For WebSocket approach:
```bash
pip install flask-sock
```

Add to `requirements.txt`:
```
flask-sock==0.7.0
```

## Configuration

```python
# server.py configuration
LIVE_CHUNK_SIZE_SECONDS = 2  # How often frontend sends chunks
MODEL_SIZE = 'base'           # Use 'tiny' for lower latency
BEAM_SIZE = 3                 # Reduce from 5 for speed
```

## Testing Plan

1. **Basic functionality:**
   - Start recording → see text appear while speaking
   - Stop recording → transcription stops

2. **Chunk handling:**
   - Verify chunks sent every 2-3 seconds
   - Check server receives and processes each chunk
   - Confirm no dropped chunks

3. **Text quality:**
   - Test for duplicate segments
   - Check boundary word accuracy
   - Verify punctuation and capitalization

4. **Latency:**
   - Measure time from speech to text appearance
   - Target: 2-4 seconds end-to-end latency
   - Test with different model sizes

5. **Error handling:**
   - Network interruption during recording
   - Server transcription errors
   - Audio device disconnection

6. **Edge cases:**
   - Very short recording (< 2 seconds)
   - Long recording (10+ minutes)
   - Rapid start/stop cycles
   - Silence periods

## Performance Optimization

### Model Selection
- **tiny**: Fastest, ~1s latency, lower accuracy
- **base**: Good balance, ~2s latency, good accuracy (recommended)
- **small**: Higher accuracy, ~3-4s latency

### Chunking Strategy
- **1-2 seconds:** Lowest latency, more boundary errors
- **2-3 seconds:** Best balance (recommended)
- **4-5 seconds:** Better accuracy, higher latency

### Concurrent Processing
```python
# Process chunks in parallel if needed
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=2)

@sock.route('/transcribe-live')
def transcribe_live_ws(ws):
    def process_chunk(audio_data):
        # Transcribe in background thread
        pass

    while True:
        audio_data = ws.receive()
        executor.submit(process_chunk, audio_data)
```

## Rollback Plan

If continuous streaming proves too complex or slow:
- Keep Task 5 implementation (post-recording streaming)
- Add "Quick Transcribe" mode: record for 5-10s → auto-stop → transcribe
- Provides faster feedback loop without full continuous streaming

## Future Enhancements

- **Voice Activity Detection (VAD):** Only send chunks with speech
- **Adaptive chunk size:** Longer chunks during continuous speech, shorter for pauses
- **Client-side buffering:** Buffer audio locally and send in batches
- **Model caching:** Keep model warm between chunks for faster processing
- **Multi-language detection:** Auto-detect language per chunk
