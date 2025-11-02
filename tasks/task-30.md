# Task 30: Word Alignment and Timestamp Preservation

- [x] Create word alignment algorithm in `llm_service.py`
- [x] Map corrected words to original word timestamps
- [x] Update `/transcribe-file` endpoint to include corrected transcript + alignment mapping
- [x] Update history display to show corrected transcript with clickable timestamps
- [x] Handle edge cases (removed filler words, merged words, word splits)
- [x] Test timestamp accuracy with corrected transcripts

**Location:** `llm_service.py`, `server.py`, `index.html`

## Context

After the LLM improves transcript readability (Task 29), we need to preserve the clickable word timestamps feature. This task creates an alignment mapping between corrected words and original words with timestamps.

## Design Notes

### Alignment Algorithm
Simple sequential matching since words are mostly preserved:

```python
def align_words(original_words, corrected_text):
    """
    Maps corrected words to original word timestamps.

    Args:
        original_words: [{"word": "so", "start": 0.0, "end": 0.2}, ...]
        corrected_text: "So I think we should go to the store."

    Returns:
        [
            {"word": "So", "start": 0.0, "end": 0.2},      # maps to "so"
            {"word": "I", "start": 0.4, "end": 0.5},       # maps to "i"
            {"word": "think", "start": 0.6, "end": 0.9},   # exact match
            ...
        ]
    """
    # 1. Split corrected text into words (preserve punctuation)
    # 2. Match sequentially using fuzzy string matching
    # 3. For removed words (um, uh), skip in corrected
    # 4. For changed words, use closest match timestamp
    # 5. For merged words, use first word's timestamp
```

### Matching Strategy
- **Exact match**: Use original timestamp
- **Case difference only**: Use original timestamp
- **Removed filler word**: Skip (don't include in corrected)
- **Changed word**: Use closest original word's timestamp (Levenshtein distance)
- **Merged words**: Use first word's timestamp
- **Split words**: Duplicate original timestamp for both parts

### API Response Format
Update `/transcribe` endpoint to return:
```json
{
  "transcription": "original raw transcript",
  "corrected_transcription": "Corrected transcript with proper grammar.",
  "language": "en",
  "duration": 5.2,
  "words": [
    {"word": "Corrected", "start": 0.0, "end": 0.3},
    {"word": "transcript", "start": 0.4, "end": 0.8},
    ...
  ]
}
```

### Frontend Updates
- Display `corrected_transcription` in history viewer
- Use `words` array for clickable timestamps
- Each word spans to its `start` time on click
- Preserve existing click-to-seek functionality
