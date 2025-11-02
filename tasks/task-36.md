# Task 36: Scrollable Text with Sticky Audio Player

- [x] Modify segment CSS to create scrollable text container
- [x] Make audio player sticky at top of segment
- [x] Add max-height constraint to text area
- [x] Ensure proper overflow handling
- [x] Test scrolling behavior with long transcripts
- **Location:** `index.html` (CSS styles and segment structure)

## Context

Currently, the segment text can overflow beyond viewable screen area without proper scrolling. The UI shows both audio player and transcription text in `.segment` divs (lines 428-485), but there's no mechanism to keep the audio player visible while scrolling through long transcriptions.

## Design

### Current Structure
```html
<div class="segment">
  <div class="segment-header">...</div>
  <audio class="segment-audio">...</audio>
  <p class="segment-text">long transcription...</p>
</div>
```

### Proposed Structure
The segment should have:
1. Fixed/sticky positioning for audio player within segment container
2. Separate scrollable div for transcription text
3. Max-height constraint on text to prevent page overflow

### CSS Changes Needed

1. **Segment container** (`.segment` at line 428):
   - Add `position: relative` to establish stacking context
   - Set reasonable max-height or height constraints

2. **Audio player** (`.segment-audio` at line 472):
   - Add `position: sticky`
   - Set `top: 0` or small offset
   - Add `z-index` to keep above text
   - Keep background color to prevent text bleed-through

3. **Text container** (`.segment-text` at line 478):
   - Wrap in scrollable div or make itself scrollable
   - Set `max-height` (e.g., 400-600px)
   - Add `overflow-y: auto`
   - Ensure proper padding/margins

### Example CSS
```css
.segment {
  position: relative;
  /* existing styles */
}

.segment-audio {
  position: sticky;
  top: 0;
  background: #ffffff;
  z-index: 10;
  /* existing styles */
}

.segment-text {
  max-height: 500px;
  overflow-y: auto;
  /* existing styles */
}
```

## Implementation Notes

- Preserve existing segment structure in JavaScript (renderClickableTranscription function at line 1610)
- Ensure sticky audio doesn't cover segment header
- Test with both short and very long transcripts
- Verify mobile responsiveness (check @media at line 736)
- Maintain existing word-click functionality (lines 1634-1644)

## Testing Checklist

- [ ] Audio player stays visible when scrolling long transcripts
- [ ] Scrollbar appears only when text exceeds max-height
- [ ] Word click functionality still works while scrolling
- [ ] Layout works on mobile devices
- [ ] Multiple segments don't interfere with each other
