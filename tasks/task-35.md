# Task 35: Add Natural Line Breaks and Paragraph Formatting to Transcript Display

- [x] Update LLM service to ensure consistent paragraph formatting (double newlines between paragraphs)
- [x] Update frontend to convert newlines to HTML line breaks for proper rendering
- [x] Update session viewer to render line breaks in saved transcripts
- [x] Ensure text rendering is safe from XSS vulnerabilities
- **Location:** `llm_service.py`, `index.html`

## Context

Currently, transcripts are displayed as one continuous block of text without visual paragraph breaks, even though the LLM adds double newlines between topics. The frontend uses `textContent` which doesn't render HTML, causing newlines to be ignored.

## Design

### LLM Service (llm_service.py)
- Verify prompt instructs LLM to add paragraph breaks with double newlines (already in place at line 42)
- Consider if additional formatting instructions are needed

### Frontend (index.html)
- Replace `textContent` with safe HTML rendering for transcript display
- Convert newlines to `<br>` tags or `<p>` tags while escaping user content
- Update affected areas:
  - Live transcription display
  - Session viewer segments (line ~1576, ~1586, ~1638)
  - History card previews (line ~1549)

### Implementation Options
1. **Option A**: Convert `\n` to `<br>` tags with HTML escaping
2. **Option B**: Split by double newlines and wrap each paragraph in `<p>` tags
3. **Option C**: Use CSS `white-space: pre-wrap` with `textContent` (preserves newlines without HTML)

Recommend Option C for simplicity and security, or Option B for semantic HTML.

## Notes
- Must prevent XSS vulnerabilities if using `innerHTML`
- Should preserve clickable word timestamps functionality from Task 28
- Test with multi-paragraph transcripts to ensure proper spacing
