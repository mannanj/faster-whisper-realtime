# Task 31: Use Corrected Transcripts in Downloads

- [ ] Update `save_transcription_files()` to use corrected transcripts
- [ ] Save corrected text in .txt download file
- [ ] Include both original and corrected transcripts in JSON download
- [ ] Test downloads contain improved grammar

**Location:** `server.py`

## Context

Currently, when users download transcriptions from the History tab, they receive the original raw transcripts instead of the LLM-corrected versions with improved grammar. This task updates the download functionality to provide the corrected transcripts.

## Design Notes

### File Saving Strategy

Update `save_transcription_files()` (server.py:91-104) to:

```python
def save_transcription_files(session_dir, segments_data, total_duration):
    # Use corrected transcripts if available, fallback to original
    full_text = " ".join([
        seg.get('corrected_transcription', seg['transcription'])
        for seg in segments_data
    ]).strip()

    # Original text for reference
    original_text = " ".join([seg['transcription'] for seg in segments_data]).strip()

    # .txt file contains corrected transcript
    txt_file = session_dir / 'transcription.txt'
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(full_text)

    # JSON contains both versions
    json_file = session_dir / 'transcription.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_duration': total_duration,
            'full_transcription': full_text,
            'original_transcription': original_text,  # Keep for reference
            'segments': segments_data
        }, f, indent=2, ensure_ascii=False)
```

### Benefits
- Downloaded .txt files contain readable, grammatically correct text
- JSON downloads include both versions for flexibility
- No breaking changes to existing data structure
- Graceful fallback if corrected_transcription is missing (backward compatible)
