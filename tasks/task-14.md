# Task 14: Fix Continuous Streaming Transcription Bug

- [x] Debug why only first word appears in transcription
- [x] Investigate if subsequent chunks are being sent to server
- [x] Check if server is processing all chunks correctly
- [x] Verify text appending logic doesn't replace previous content
- [x] Add logging to track chunk processing pipeline
- [x] Test with longer continuous speech (10+ seconds)
- [x] Ensure chunks don't overlap/duplicate transcription
- **Location:** `index.html`, `server.py`

## Problem Description

When starting recording, only the first word (e.g., "Testing") appears in the transcription box. Subsequent audio chunks are being recorded (MediaRecorder sends chunks every 2 seconds), but the transcription text doesn't update with new content.

## Expected Behavior

- User clicks "Enable Microphone" and starts speaking
- First chunk (2s) → "Testing" appears
- Second chunk (2s) → "this is" appends → "Testing this is"
- Third chunk (2s) → "a demo" appends → "Testing this is a demo"
- Transcription continues to append as long as user speaks

## Actual Behavior

- User clicks "Enable Microphone" and starts speaking
- First chunk (2s) → "Testing" appears
- Second chunk (2s) → Nothing appends
- Third chunk (2s) → Nothing appends
- Only "Testing" remains visible

## Potential Root Causes

### 1. Frontend Text Replacement Issue
**Hypothesis:** The `appendTranscription()` function might be inadvertently replacing text instead of appending.

**Current Code (index.html:414-421):**
```javascript
function appendTranscription(text) {
    if (transcription.classList.contains('empty')) {
        transcription.classList.remove('empty');
        transcription.textContent = '';
    }
    transcription.textContent += ' ' + text;
    transcription.scrollTop = transcription.scrollHeight;
}
```

**Potential Issue:** If `transcription.classList.contains('empty')` evaluates to true on subsequent chunks, it clears the text.

**Fix:** Ensure empty class is only removed once, or check if textContent is truly empty.

### 2. Chunk Processing Not Completing
**Hypothesis:** The SSE stream from `/transcribe-live` might not be completing properly, causing subsequent chunks to hang.

**Debug Steps:**
- Add `console.log()` statements in `sendChunkForTranscription()` to track:
  - When chunk is sent
  - When response is received
  - When segments are parsed
  - When `appendTranscription()` is called

### 3. Server-Side Transcription Errors
**Hypothesis:** The server might be failing to transcribe chunks after the first one (e.g., WebM chunk format issues).

**Debug Steps:**
- Check server logs for errors during chunk processing
- Verify each chunk file is valid WebM format
- Test if faster-whisper can transcribe individual chunk files

### 4. Audio Chunk Size/Format Issues
**Hypothesis:** Audio chunks after the first might be too small, corrupted, or in a format faster-whisper can't process.

**Debug Steps:**
- Log `event.data.size` for each chunk
- Save chunks to disk temporarily to verify format
- Test chunks manually with faster-whisper CLI

### 5. Race Condition with Concurrent Requests
**Hypothesis:** Multiple `/transcribe-live` POST requests might be interfering with each other.

**Potential Issue:** If chunk 2 starts processing before chunk 1 completes, responses might get mixed up.

**Fix:**
- Queue chunks sequentially instead of parallel processing
- Add request tracking with chunk_index validation

### 6. MediaRecorder State Issues
**Hypothesis:** MediaRecorder might stop after first chunk due to state changes.

**Debug Steps:**
- Log `mediaRecorder.state` before and after each chunk
- Check if `isRecording` flag remains true
- Verify `dataavailable` event fires multiple times

## Debugging Plan

### Step 1: Add Frontend Logging
```javascript
async function sendChunkForTranscription(audioBlob) {
    console.log(`[Chunk ${chunkCounter}] Sending chunk, size: ${audioBlob.size} bytes`);

    const formData = new FormData();
    formData.append('audio', audioBlob, 'chunk.webm');
    formData.append('chunk_index', chunkCounter);
    formData.append('session_id', sessionId);

    const currentChunkIndex = chunkCounter;
    chunkCounter++;

    try {
        console.log(`[Chunk ${currentChunkIndex}] Fetch started`);
        const response = await fetch('/transcribe-live', {
            method: 'POST',
            body: formData
        });

        console.log(`[Chunk ${currentChunkIndex}] Response received`);

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                console.log(`[Chunk ${currentChunkIndex}] Stream complete`);
                break;
            }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n\n');
            buffer = lines.pop();

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));
                    console.log(`[Chunk ${currentChunkIndex}] Received:`, data);

                    if (data.type === 'segment') {
                        console.log(`[Chunk ${currentChunkIndex}] Appending text: "${data.text}"`);
                        appendTranscription(data.text);
                    }
                }
            }
        }

    } catch (error) {
        console.error(`[Chunk ${currentChunkIndex}] Error:`, error);
    }
}

function appendTranscription(text) {
    console.log(`appendTranscription called with: "${text}"`);
    console.log(`Current content: "${transcription.textContent}"`);

    if (transcription.classList.contains('empty')) {
        transcription.classList.remove('empty');
        transcription.textContent = '';
    }
    transcription.textContent += ' ' + text;

    console.log(`New content: "${transcription.textContent}"`);
    transcription.scrollTop = transcription.scrollHeight;
}
```

### Step 2: Add Server Logging
```python
@app.route('/transcribe-live', methods=['POST'])
def transcribe_live():
    chunk_index = request.form.get('chunk_index', 0)
    session_id = request.form.get('session_id', 'default')

    print(f"\n[Server] Received chunk {chunk_index} for session {session_id}")

    if 'audio' not in request.files:
        return jsonify({'error': 'No audio chunk provided'}), 400

    audio_chunk = request.files['audio']
    print(f"[Server] Chunk {chunk_index} size: {len(audio_chunk.read())} bytes")
    audio_chunk.seek(0)  # Reset file pointer after reading size

    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
        audio_chunk.save(temp_audio.name)
        temp_path = temp_audio.name

    def generate_segments():
        try:
            print(f"[Server] Transcribing chunk {chunk_index}...")
            segments, info = model.transcribe(temp_path, beam_size=5)

            if int(chunk_index) == 0:
                print(f"[Server] Chunk {chunk_index} metadata: language={info.language}")
                yield f"data: {json.dumps({'type': 'metadata', 'language': info.language})}\n\n"

            segment_count = 0
            for segment in segments:
                segment_count += 1
                print(f"[Server] Chunk {chunk_index} segment {segment_count}: {segment.text}")
                yield f"data: {json.dumps({'type': 'segment', 'start': segment.start, 'end': segment.end, 'text': segment.text})}\n\n"

            print(f"[Server] Chunk {chunk_index} complete ({segment_count} segments)")
            yield f"data: {json.dumps({'type': 'chunk_complete', 'chunk_index': chunk_index})}\n\n"

        except Exception as e:
            print(f"[Server] Error transcribing chunk {chunk_index}: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    return Response(stream_with_context(generate_segments()), mimetype='text/event-stream')
```

### Step 3: Test Scenarios

1. **Single word test:**
   - Speak one word every 3 seconds
   - Expected: Each word appears sequentially

2. **Continuous speech test:**
   - Speak continuously for 10 seconds
   - Expected: All words appear as chunks process

3. **Silence test:**
   - Speak for 2s, pause 5s, speak for 2s
   - Expected: First chunk transcribes, silence produces no text, second chunk transcribes

4. **MediaRecorder state test:**
   - Log `mediaRecorder.state` every 500ms
   - Expected: State should remain "recording" throughout

## Expected Fixes

Based on common issues with this pattern:

### Fix 1: Prevent Empty Class from Clearing Text
```javascript
function appendTranscription(text) {
    // Only clear if truly empty (first time)
    if (transcription.textContent === 'Speak to start transcribing...') {
        transcription.textContent = '';
        transcription.classList.remove('empty');
    }

    transcription.textContent += ' ' + text;
    transcription.scrollTop = transcription.scrollHeight;
}
```

### Fix 2: Ensure MediaRecorder Continues
```javascript
function startRecording() {
    if (!mediaStream) return;

    mediaRecorder = new MediaRecorder(mediaStream);
    chunkCounter = 0;

    // Clear text only on first start
    if (transcription.textContent === 'Speak to start transcribing...') {
        transcription.textContent = '';
        transcription.classList.remove('empty');
    }

    mediaRecorder.addEventListener('dataavailable', async (event) => {
        console.log(`MediaRecorder dataavailable: size=${event.data.size}, state=${mediaRecorder.state}`);

        if (event.data.size > 0 && isRecording && !isMuted) {
            await sendChunkForTranscription(event.data);
        }
    });

    mediaRecorder.start(2000);
    isRecording = true;

    console.log('MediaRecorder started with 2s timeslice');
}
```

### Fix 3: Handle Empty Transcriptions
```python
# In server.py generate_segments()
segment_count = 0
for segment in segments:
    if segment.text.strip():  # Only send non-empty segments
        segment_count += 1
        print(f"[Server] Chunk {chunk_index} segment {segment_count}: {segment.text}")
        yield f"data: {json.dumps({'type': 'segment', 'start': segment.start, 'end': segment.end, 'text': segment.text})}\n\n"
```

## Validation Criteria

- [ ] Console logs show chunks being sent every 2 seconds
- [ ] Server logs show chunks being received and transcribed
- [ ] Each chunk produces at least one segment (if audio contains speech)
- [ ] Frontend appends text without clearing previous content
- [ ] Transcription box shows cumulative text from all chunks
- [ ] Test with 10+ seconds of continuous speech
- [ ] Test with intermittent speech (word, pause, word, pause)
- [ ] Verify no duplicate text appears

## Performance Considerations

- Monitor transcription latency (time from chunk sent to text appears)
- Target: < 3 seconds per chunk
- If latency too high, consider:
  - Switching to `tiny` model
  - Reducing beam_size from 5 to 3
  - Increasing chunk duration from 2s to 3s

## Rollback Plan

If continuous streaming proves unreliable:
- Revert to Task 5 implementation (single recording → transcribe after stop)
- Keep Task 13 UI (orb visualization) but add explicit start/stop via orb clicks
- Alternative: Batch chunks and send every 10 seconds instead of 2 seconds
