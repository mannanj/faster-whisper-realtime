# Task 28: Add Clickable Word Timestamps in History Viewer

- [ ] Update `viewSession()` to render words as clickable elements with timestamps
- [ ] Add CSS styles for clickable words (hover effects, cursor pointer)
- [ ] Implement click handler to seek audio to word's timestamp
- [ ] Update segment display in File Upload tab to use same clickable word rendering
- [ ] Add visual feedback when clicking words (highlight, active state)
- **Location:** `index.html`

## Context

Currently, the transcription text in the history viewer and file upload segments displays as plain text. However, we now have word-level timestamps from Task 26 that include the exact start/end time for each word. Users want to click on any word in the transcription to jump the audio player to that specific moment.

## Design

### 1. Word Rendering

Instead of displaying transcription as plain text, render each word as an interactive element:

```html
<!-- Current (plain text) -->
<p class="segment-text">Hi guys, where is everyone?</p>

<!-- New (clickable words) -->
<p class="segment-text">
  <span class="word" data-start="0.0" data-end="0.2">Hi</span>
  <span class="word" data-start="0.2" data-end="0.5">guys,</span>
  <span class="word" data-start="0.5" data-end="0.8">where</span>
  ...
</p>
```

### 2. CSS Styling

Add styles for interactive words:

```css
.word {
    cursor: pointer;
    transition: all 0.15s ease;
    padding: 2px 1px;
    border-radius: 3px;
}

.word:hover {
    background: #f5f5f5;
    color: #000000;
}

.word.active {
    background: #000000;
    color: #ffffff;
}
```

### 3. Click Handler Implementation

Add JavaScript to handle word clicks and seek audio:

```javascript
function renderClickableTranscription(segment, audioElement) {
    if (!segment.words || segment.words.length === 0) {
        return segment.transcription;
    }

    const container = document.createElement('p');
    container.className = 'segment-text';

    segment.words.forEach((wordData, index) => {
        const wordSpan = document.createElement('span');
        wordSpan.className = 'word';
        wordSpan.textContent = wordData.word;
        wordSpan.dataset.start = wordData.start;
        wordSpan.dataset.end = wordData.end;

        wordSpan.addEventListener('click', () => {
            audioElement.currentTime = wordData.start;
            audioElement.play();

            // Visual feedback
            document.querySelectorAll('.word.active').forEach(w => w.classList.remove('active'));
            wordSpan.classList.add('active');

            // Remove active state after word duration
            setTimeout(() => {
                wordSpan.classList.remove('active');
            }, (wordData.end - wordData.start) * 1000);
        });

        container.appendChild(wordSpan);

        // Add space between words (preserve original spacing)
        if (index < segment.words.length - 1) {
            container.appendChild(document.createTextNode(' '));
        }
    });

    return container;
}
```

### 4. Integration Points

**A. History Viewer (`viewSession` function - line 1548)**

Update the segment rendering to use clickable words:

```javascript
// Find the audio element
const audio = segmentDiv.querySelector('.segment-audio');

// Render clickable transcription if words are available
if (segment.words && segment.words.length > 0) {
    const textContainer = renderClickableTranscription(segment, audio);
    const textElement = segmentDiv.querySelector('.segment-text');
    textElement.replaceWith(textContainer);
}
```

**B. File Upload Tab (`addSegment` function - line 1357)**

Similarly update the real-time segment display:

```javascript
// After adding segment HTML
const audio = segmentDiv.querySelector('.segment-audio');

// Once we have word data (may come later via status updates)
// Replace text with clickable version
if (data.words && data.words.length > 0) {
    const textContainer = renderClickableTranscription({words: data.words}, audio);
    const textElement = segmentDiv.querySelector('.segment-text');
    textElement.replaceWith(textContainer);
}
```

### 5. Fallback for Missing Word Data

If `words` array is not available (older sessions, or word_timestamps=false), display plain text as before:

```javascript
function renderTranscription(segment, audioElement) {
    if (segment.words && segment.words.length > 0) {
        return renderClickableTranscription(segment, audioElement);
    } else {
        // Fallback to plain text
        const p = document.createElement('p');
        p.className = 'segment-text';
        p.textContent = segment.transcription || '';
        return p;
    }
}
```

### 6. Enhanced User Experience Features (Optional)

- **Active word highlighting during playback**: Track audio.currentTime and highlight the current word
- **Hover preview**: Show timestamp on hover (e.g., "0:00.5")
- **Confidence indicator**: Use word.probability to fade low-confidence words

## Implementation Steps

1. Add CSS styles for `.word`, `.word:hover`, `.word.active`
2. Create `renderClickableTranscription()` helper function
3. Update `viewSession()` to use clickable rendering for history
4. Update `addSegment()` to use clickable rendering for new uploads
5. Test with existing sessions that have word timestamp data
6. Verify fallback works for sessions without word data

## Success Criteria

- Clicking any word in the history viewer seeks the audio to that word's timestamp
- Words have hover effect to indicate they're clickable
- Active word is visually highlighted when clicked
- Works for both history viewer and current upload segments
- Gracefully falls back to plain text when word data is unavailable
- Audio automatically plays when word is clicked
