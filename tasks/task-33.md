# Task 33: (Optional) Add LLM Correction to Live Streaming Tab

- [ ] Add LLM correction to `/transcribe-live` endpoint
- [ ] Handle streaming chunks with LLM correction
- [ ] Display corrected text in live streaming UI
- [ ] Consider batching strategy for streaming

**Location:** `server.py`, `index.html`

## Context

The Live Streaming tab (for continuous recording) currently only shows raw Whisper transcripts. This task adds LLM correction, but requires careful handling of streaming chunks.

## Design Notes

### Streaming Challenges

⚠️ **Complexity:**
- Live streaming sends audio chunks every 3 seconds
- LLM correction takes 2-5 seconds per chunk
- Risk of corrections arriving out-of-order
- May create confusing UX if text keeps changing

### Recommended Approach: Batch Correction

Instead of correcting each 3-second chunk individually:

1. **Accumulate chunks** - Store raw transcripts as they arrive
2. **Show raw text immediately** - Display Whisper output with no delay
3. **Batch correction** - Every 30-60 seconds, correct the accumulated text
4. **Update display** - Replace raw text with corrected version in batches

```python
# Pseudocode
accumulated_text = []
last_correction_time = time.time()

for chunk in audio_chunks:
    raw_text = whisper.transcribe(chunk)
    accumulated_text.append(raw_text)

    # Show raw immediately
    yield raw_text

    # Correct in batches every 60 seconds
    if time.time() - last_correction_time > 60:
        full_text = " ".join(accumulated_text)
        corrected = llm_service.correct_transcript(full_text)
        yield corrected
        last_correction_time = time.time()
```

### Alternative: Post-Recording Correction

Simpler approach:
- Show raw transcripts during live recording
- After user stops recording, apply LLM correction to entire transcript
- Display "Improving transcript..." message
- Update with corrected version

This avoids streaming complexity while still providing improved readability.

### UI Considerations
- Show indicator when correction is happening
- Consider "Finalize" button to trigger correction
- Allow users to disable correction for truly real-time use
