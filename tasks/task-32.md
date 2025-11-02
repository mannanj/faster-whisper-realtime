# Task 32: (Optional) Add LLM Correction to Real-time Tab

- [ ] Add LLM correction to `/transcribe` endpoint
- [ ] Display corrected transcript in real-time UI
- [ ] Add loading indicator for LLM processing
- [ ] Consider latency impact on user experience

**Location:** `server.py`, `index.html`

## Context

The Real-time tab (for quick voice recordings) currently only shows raw Whisper transcripts. This task adds LLM correction to improve readability, but comes with a latency trade-off.

## Design Notes

### Latency Considerations

⚠️ **Important Trade-off:**
- Whisper transcription: ~1-3 seconds
- LLM correction: ~2-5 seconds
- **Total delay: ~3-8 seconds**

This may feel slow for "real-time" recordings. Consider:
1. Making LLM correction **optional** (toggle in UI)
2. Showing raw transcript immediately, then updating with corrected version
3. Adding a progress indicator during LLM processing

### Implementation Options

**Option A: Progressive Display (Recommended)**
```javascript
// Show raw transcript immediately
displayTranscript(rawText);

// Then fetch and display corrected version
const corrected = await fetchLLMCorrection(rawText);
updateTranscript(corrected);
```

**Option B: Toggle Button**
```html
<label>
  <input type="checkbox" id="enableLLMCorrection">
  Improve grammar (adds ~3s delay)
</label>
```

### Backend Changes

Update `/transcribe` endpoint (server.py:347-381):
```python
# After transcription completes
full_text = " ".join([seg.text for seg in segments]).strip()

# Apply LLM correction if enabled
corrected_text = llm_service.correct_transcript(full_text)

yield f"data: {json.dumps({'type': 'corrected', 'text': corrected_text})}\n\n"
```

### UI Considerations
- Show "Improving transcript..." message during LLM processing
- Display both raw and corrected versions?
- Allow users to toggle between versions?
