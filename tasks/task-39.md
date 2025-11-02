# Task 39: Smart Auto-Scroll with "Return to Live" Floating Indicator

- [ ] Detect user scrolling vs auto-scroll
- [ ] Show/hide floating indicator based on scroll state
- [ ] Position indicator (top/bottom) based on active word location
- [ ] Implement "return to live" functionality on indicator click
- [ ] Add smooth animations for indicator appearance/disappearance
- [ ] Style indicator to match existing design system
- **Location:** `index.html` (renderClickableTranscription function, CSS)

## Context

Currently, we have a checkbox to toggle auto-scroll on/off. While functional, it requires manual toggling and doesn't provide spatial awareness of where the "live" active word is when browsing.

A floating "Return to Live" indicator provides a more intuitive UX:
- Appears automatically when user scrolls away from active word
- Shows direction to active word (up/down arrow)
- Click to jump back and resume auto-scroll
- Hides when in auto-lock mode (following along)

## Design

### Behavior States

**Auto-Lock Mode (Default):**
- Audio plays, word highlights, auto-scroll follows
- Indicator hidden
- This is the "following along" state

**Browse Mode (User Scrolled):**
- User manually scrolls away from active word
- Auto-scroll pauses
- Indicator appears with directional arrow
- Active word still highlights (just not visible)
- User can read ahead or review past text

**Return to Live:**
- User clicks indicator
- Smooth scroll to active word
- Resume auto-lock mode
- Indicator fades out

### Scroll Detection Strategy

Need to distinguish between:
1. **Auto-scroll** (triggered by timeupdate event)
2. **User scroll** (manual interaction)

**Implementation approach:**
```javascript
let isAutoScrolling = false;

// Before auto-scroll
isAutoScrolling = true;
wordSpan.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
setTimeout(() => isAutoScrolling = false, 200);

// On scroll event
container.addEventListener('scroll', (e) => {
    if (!isAutoScrolling) {
        // User is scrolling - enter browse mode
        enterBrowseMode();
    }
});
```

### Indicator Design

**Visual Style (Floating Arrow Pill):**
- Black background, white text (matches `.word.active` style)
- Rounded pill shape: `border-radius: 24px`
- Subtle shadow for elevation
- Arrow icon (↑ or ↓) + text
- Semi-transparent so underlying text is slightly visible

**Positioning:**
- `position: sticky` within transcript container
- `top: 10px` if active word is above viewport (show ↑)
- `bottom: 10px` if active word is below viewport (show ↓)
- `left: 50%; transform: translateX(-50%)` for centering
- `z-index: 10` to float above text

**Content:**
- If active word above: `↑ Return to live`
- If active word below: `↓ Return to live`
- Alternative shorter text: `↑ Live` or `🔴 Live`

**Animation:**
```css
@keyframes slideInTop {
    from { transform: translate(-50%, -100%); opacity: 0; }
    to { transform: translate(-50%, 0); opacity: 1; }
}

@keyframes slideInBottom {
    from { transform: translate(-50%, 100%); opacity: 0; }
    to { transform: translate(-50%, 0); opacity: 1; }
}

.live-indicator {
    animation: slideInTop 0.3s ease;
}

.live-indicator.below {
    animation: slideInBottom 0.3s ease;
}
```

Optional: Gentle pulse animation to draw attention
```css
@keyframes pulse {
    0%, 100% { transform: translate(-50%, 0) scale(1); }
    50% { transform: translate(-50%, 0) scale(1.02); }
}
```

### Implementation Steps

#### 1. Add HTML structure for indicator

Create indicator element dynamically when entering browse mode:
```javascript
function createLiveIndicator(direction) {
    const indicator = document.createElement('div');
    indicator.className = `live-indicator ${direction}`;
    indicator.innerHTML = `
        ${direction === 'above' ? '↑' : '↓'} Return to live
    `;
    indicator.addEventListener('click', returnToLive);
    return indicator;
}
```

#### 2. Add CSS styles

```css
.live-indicator {
    position: sticky;
    left: 50%;
    transform: translateX(-50%);
    background: #000000;
    color: #ffffff;
    padding: 10px 20px;
    border-radius: 24px;
    font-size: 14px;
    font-weight: 400;
    cursor: pointer;
    z-index: 10;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    user-select: none;
    white-space: nowrap;
}

.live-indicator.above {
    top: 10px;
    animation: slideInTop 0.3s ease;
}

.live-indicator.below {
    bottom: 10px;
    animation: slideInBottom 0.3s ease;
}

.live-indicator:hover {
    background: #333333;
}
```

#### 3. Modify renderClickableTranscription

Add scroll detection and state management:
```javascript
function renderClickableTranscription(segment, audioElement) {
    // ... existing word creation code ...

    let isAutoScrolling = false;
    let browseMode = false;
    let liveIndicator = null;

    // Scroll detection
    container.addEventListener('scroll', () => {
        if (!isAutoScrolling && audioElement && !audioElement.paused) {
            enterBrowseMode();
        }
    });

    function enterBrowseMode() {
        if (browseMode) return;
        browseMode = true;
        showLiveIndicator();
    }

    function exitBrowseMode() {
        browseMode = false;
        hideLiveIndicator();
    }

    function showLiveIndicator() {
        const activeWord = container.querySelector('.word.active');
        if (!activeWord) return;

        const direction = isWordAboveViewport(activeWord) ? 'above' : 'below';
        liveIndicator = createLiveIndicator(direction);
        container.prepend(liveIndicator);
    }

    function hideLiveIndicator() {
        if (liveIndicator) {
            liveIndicator.remove();
            liveIndicator = null;
        }
    }

    function returnToLive() {
        const activeWord = container.querySelector('.word.active');
        if (activeWord) {
            isAutoScrolling = true;
            activeWord.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            setTimeout(() => isAutoScrolling = false, 500);
        }
        exitBrowseMode();
    }

    function isWordAboveViewport(element) {
        const rect = element.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();
        return rect.top < containerRect.top;
    }

    // Modify existing timeupdate listener
    audioElement.addEventListener('timeupdate', () => {
        const currentTime = audioElement.currentTime;
        const allWords = container.querySelectorAll('.word');

        allWords.forEach(wordSpan => {
            const start = parseFloat(wordSpan.dataset.start);
            const end = parseFloat(wordSpan.dataset.end);

            if (currentTime >= start && currentTime < end) {
                allWords.forEach(w => w.classList.remove('active'));
                wordSpan.classList.add('active');

                // Only auto-scroll if not in browse mode
                if (!browseMode && localStorage.getItem('autoScrollEnabled') !== 'false') {
                    isAutoScrolling = true;
                    wordSpan.scrollIntoView({
                        behavior: 'smooth',
                        block: 'nearest'
                    });
                    setTimeout(() => isAutoScrolling = false, 200);
                }

                // Update indicator direction if visible
                if (browseMode && liveIndicator) {
                    const newDirection = isWordAboveViewport(wordSpan) ? 'above' : 'below';
                    const currentDirection = liveIndicator.classList.contains('above') ? 'above' : 'below';
                    if (newDirection !== currentDirection) {
                        hideLiveIndicator();
                        showLiveIndicator();
                    }
                }
            }
        });
    });

    // Clean up on pause/end
    audioElement.addEventListener('pause', () => {
        exitBrowseMode();
        container.querySelectorAll('.word.active').forEach(w =>
            w.classList.remove('active')
        );
    });

    audioElement.addEventListener('ended', () => {
        exitBrowseMode();
        container.querySelectorAll('.word.active').forEach(w =>
            w.classList.remove('active')
        );
    });

    return container;
}
```

### Edge Cases

1. **Multiple audio players**: Each segment has its own indicator state
2. **Rapid scrolling**: Debounce indicator updates
3. **Active word at viewport edge**: Use `block: 'nearest'` for smart positioning
4. **Touch scrolling**: Works same as mouse scroll
5. **Keyboard scrolling**: PageUp/PageDown should trigger browse mode
6. **Audio seeking**: Should maintain current mode (browse or auto-lock)
7. **Very short segments**: Indicator might not be needed if all text is visible
8. **Indicator position switching**: Update smoothly when active word crosses viewport

### Performance Considerations

- Throttle scroll event to avoid excessive checks
- Cache active word element reference
- Use `requestAnimationFrame` for smooth updates
- Remove indicator from DOM when not needed (not just hide)

### Accessibility

- Ensure indicator is keyboard accessible (tab focus)
- Add ARIA label: `aria-label="Return to live transcription"`
- Support Enter/Space to activate
- Screen reader should announce when entering/exiting browse mode

### Testing Checklist

- [ ] Indicator appears when user scrolls away from active word
- [ ] Arrow direction correctly indicates active word position
- [ ] Click indicator smoothly scrolls to active word
- [ ] Indicator disappears after returning to live
- [ ] Indicator doesn't appear during auto-scroll
- [ ] Works with both File Upload tab and History viewer
- [ ] Multiple audio players don't interfere with each other
- [ ] Pause/end events properly clean up indicator
- [ ] Keyboard navigation works
- [ ] Touch scrolling triggers browse mode
- [ ] Performance is smooth with long transcripts

## Relationship to Existing Features

This feature builds on Task 37 (Active Word Highlighting). It can work:
- **Standalone**: Replace the checkbox entirely
- **Together**: Checkbox as master switch, indicator for navigation
- **Hybrid**: Checkbox hidden in settings, indicator as primary UX

Recommend: Keep the checkbox for now, add indicator as enhancement. Can remove checkbox in future if indicator proves sufficient.

## Future Enhancements

- Show distance to active word: "↑ 12 words behind"
- Pulse animation on indicator
- Different color when far away vs close
- Keyboard shortcut to return to live (e.g., Ctrl+L)
- Mini preview of active word text in indicator
