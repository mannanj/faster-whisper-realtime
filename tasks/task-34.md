# Task 34: Display Corrected Transcripts Throughout Frontend

- [ ] Update `addSegment()` to capture corrected_transcription from server response
- [ ] Update copy buttons to use corrected transcript instead of original
- [ ] Update `copySegment()` function to prefer corrected_transcription
- [ ] Update history viewer copy button to use corrected transcript
- [ ] Test all transcript displays show corrected text

**Location:** `index.html`

## Context

The frontend currently displays corrected transcripts in the History viewer (via `renderClickableTranscription`), but there are several places where the original transcripts are still being used:

1. File Upload results page doesn't capture corrected_transcription data
2. Copy buttons use original transcripts instead of corrected versions
3. The segment object doesn't include the corrected field

## Issues to Fix

### 1. File Upload Results - addSegment() function (line 1374-1412)

**Problem:** Line 1377 only captures original transcription
```javascript
const segment = {
    index: data.segment,
    transcription: data.transcription,  // Only original
    start_time: data.start_time,
    end_time: data.end_time,
    words: data.words
};
```

**Fix:**
```javascript
const segment = {
    index: data.segment,
    transcription: data.transcription,
    corrected_transcription: data.corrected_transcription,  // Add this
    start_time: data.start_time,
    end_time: data.end_time,
    words: data.words
};
```

### 2. Copy Buttons - Use Corrected Text

**Problem:** copySegment function (line 1432-1442) uses original:
```javascript
async function copySegment(index, button) {
    const segment = allSegments.find(s => s.index === index);
    if (!segment || !segment.transcription) return;

    try {
        await navigator.clipboard.writeText(segment.transcription);  // Wrong
```

**Fix:**
```javascript
async function copySegment(index, button) {
    const segment = allSegments.find(s => s.index === index);
    if (!segment) return;

    const text = segment.corrected_transcription || segment.transcription;
    if (!text) return;

    try {
        await navigator.clipboard.writeText(text);
```

### 3. History Viewer Copy Button (line 1636)

**Problem:** Inline onclick uses original:
```javascript
<button class="segment-copy" onclick="copySegmentText('${segment.transcription}', this)">Copy</button>
```

**Fix:**
```javascript
<button class="segment-copy" onclick="copySegmentText('${segment.corrected_transcription || segment.transcription}', this)">Copy</button>
```

### 4. Server Response Check

Verify server is sending corrected_transcription in segment_complete event:
```python
# server.py line 219
yield f"data: {json.dumps({
    'type': 'segment_complete',
    'segment': idx,
    'transcription': transcription_text,
    'corrected_transcription': corrected_text,  # Add this if missing
    'start_time': segment_info['start_time'],
    'end_time': segment_info['end_time']
})}\n\n"
```

## Expected Behavior After Fix

✅ File upload results show corrected grammar immediately
✅ Copy buttons copy corrected text (with proper punctuation)
✅ History viewer displays corrected text
✅ All segment displays use improved transcripts
✅ Graceful fallback to original if corrected not available
