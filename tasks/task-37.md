# Task 37: Active Word Highlighting During Audio Playback

- [ ] Add timeupdate event listener to audio elements
- [ ] Implement word highlighting based on playback time
- [ ] Clear highlighting when audio pauses/stops
- [ ] Handle edge cases (seeking, speed changes)
- [ ] Add smooth visual feedback for active word
- **Location:** `index.html` (JavaScript audio event handlers)

## Context

Currently, clicking a word jumps to that timestamp and briefly highlights it (lines 1634-1644). However, there's no real-time highlighting as the audio plays naturally. Users can't see which word is being spoken at any given moment during continuous playback.

The word data includes start/end timestamps:
```javascript
{
  word: "example",
  start: 1.23,
  end: 1.56
}
```

## Design

### Event-Driven Highlighting

1. **Listen to audio timeupdate events**
   - Fires during playback (~4 times per second)
   - Provides `audioElement.currentTime`

2. **Find matching word**
   - Iterate through word spans in segment
   - Compare `currentTime` with `word.start` and `word.end`
   - Highlight word if `start <= currentTime < end`

3. **Update visual state**
   - Add `.active` class to current word
   - Remove `.active` from previous word
   - Auto-scroll text to keep active word visible

### Implementation Areas

#### 1. Modify renderClickableTranscription (line 1610)
Add timeupdate listener when creating segment:

```javascript
function renderClickableTranscription(segment, audioElement) {
  // ... existing word creation code ...

  // Add playback tracking
  audioElement.addEventListener('timeupdate', () => {
    const currentTime = audioElement.currentTime;
    const allWords = container.querySelectorAll('.word');

    allWords.forEach(wordSpan => {
      const start = parseFloat(wordSpan.dataset.start);
      const end = parseFloat(wordSpan.dataset.end);

      if (currentTime >= start && currentTime < end) {
        // Clear previous active
        allWords.forEach(w => w.classList.remove('active'));
        // Highlight current
        wordSpan.classList.add('active');
        // Auto-scroll to keep word visible
        wordSpan.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest'
        });
      }
    });
  });

  // Clear highlighting when paused/ended
  audioElement.addEventListener('pause', () => {
    container.querySelectorAll('.word.active').forEach(w =>
      w.classList.remove('active')
    );
  });

  audioElement.addEventListener('ended', () => {
    container.querySelectorAll('.word.active').forEach(w =>
      w.classList.remove('active')
    );
  });

  return container;
}
```

#### 2. Apply to all segment rendering locations
- addSegment function (line 1376)
- viewSession function (line 1661)
- Both use renderClickableTranscription, so one change covers both

#### 3. Performance considerations
- Use binary search for word lookup if segments have 100+ words
- Debounce scrollIntoView to avoid jank
- Consider caching word array for faster lookup

### CSS Enhancement

The `.word.active` style already exists (lines 504-507):
```css
.word.active {
    background: #000000;
    color: #ffffff;
}
```

May want to add transition for smoother highlighting:
```css
.word {
    transition: background-color 0.15s ease, color 0.15s ease;
}
```

## Edge Cases

1. **Seeking**: When user seeks ahead, highlighting should jump immediately
   - timeupdate handles this automatically

2. **Playback speed**: Different speeds shouldn't affect highlighting
   - currentTime is absolute, not relative to playback rate

3. **Multiple audio players**: Only highlight words for actively playing audio
   - Each audio element has its own listener
   - Pause event clears highlighting

4. **Word boundaries**: Handle gaps between words gracefully
   - If `currentTime` doesn't match any word, no highlighting
   - Previous word stays highlighted until next word starts

## Testing Checklist

- [ ] Words highlight automatically during playback
- [ ] Only one word highlighted at a time
- [ ] Highlighting clears when audio pauses
- [ ] Seeking to different time highlights correct word
- [ ] Auto-scroll keeps highlighted word visible
- [ ] Manual word clicks still work (don't break existing feature)
- [ ] Works in both File Upload tab and History viewer
- [ ] Performance is smooth with long transcripts (500+ words)
