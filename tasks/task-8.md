# Task 8: Interactive Audio Player with Transcript Sync

- [ ] Create `/player/<recording_id>` route for detailed playback view
- [ ] Design beautiful audio player UI with waveform visualization (optional)
- [ ] Display full transcription with segment highlighting
- [ ] Implement click-to-jump: click any segment → audio jumps to timestamp
- [ ] Implement auto-highlight: highlight current segment as audio plays
- [ ] Add playback controls (play/pause, seek, speed, volume)
- [ ] Show current time and total duration
- [ ] Add keyboard shortcuts (space = play/pause, left/right = seek)
- [ ] Handle multi-chunk recordings seamlessly
- [ ] Add copy transcription to clipboard button
- [ ] Match gradient design theme from main app
- **Location:** `server.py` (new route), new `player.html` file

## Purpose
Create a slick, beautiful audio player with synchronized transcript navigation, allowing users to click any part of the transcript to jump to that moment in the audio and see real-time highlighting as audio plays.

## UI Design

### Layout
```
┌───────────────────────────────────────────────────────┐
│  🎙️ Recording Player                                  │
│  ← Back to Library                                    │
│                                                         │
│  📅 October 27, 2025 • 14:30:45                        │
│  🌐 English • ⏱️ 2m 25s                                │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │         [Waveform Visualization]                 │  │
│  │  ━━━━━━━━━━━━━━●━━━━━━━━━━━━━━━━━━━━━━━━━━━    │  │
│  │         1:23 / 2:25                              │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  ⏮️  ◀◀  ▶️  ▶▶  ⏭️    🔊 ━━━━━●━━    1x  📋   │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  📝 Transcript                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │                                                   │  │
│  │  [0:00] Hello world this is a test               │  │
│  │  [0:03] ▶ Another segment here that is          │  │
│  │         currently playing and highlighted        │  │
│  │  [0:08] More transcription text continues        │  │
│  │  [0:12] Click any segment to jump there          │  │
│  │                                                   │  │
│  └─────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────┘
```

### Visual Design
- Same purple gradient background
- White container card with audio player
- Transcript segments in individual clickable cards
- Current segment: Highlighted with gradient background + bold text
- Hover state: Subtle highlight to indicate clickability
- Smooth transitions for all state changes

## Key Features

### 1. Clickable Transcript Navigation
```javascript
// Click segment → jump to timestamp
transcriptSegment.addEventListener('click', (e) => {
  const timestamp = e.target.dataset.timestamp;
  audioElement.currentTime = timestamp;
  audioElement.play();
});
```

### 2. Auto-Highlight Current Segment
```javascript
// Listen to audio timeupdate event
audioElement.addEventListener('timeupdate', () => {
  const currentTime = audioElement.currentTime;

  // Find current segment
  const currentSegment = segments.find(s =>
    currentTime >= s.start && currentTime < s.end
  );

  // Update UI highlighting
  highlightSegment(currentSegment);
  scrollToSegment(currentSegment);
});
```

### 3. Playback Controls
- Play/Pause button with smooth icon transition
- Seek bar with progress indicator
- Skip forward/backward 10 seconds
- Playback speed control (0.5x, 0.75x, 1x, 1.25x, 1.5x, 2x)
- Volume control slider
- Copy full transcript to clipboard

### 4. Keyboard Shortcuts
```javascript
document.addEventListener('keydown', (e) => {
  switch(e.code) {
    case 'Space': togglePlayPause(); break;
    case 'ArrowLeft': skipBackward(10); break;
    case 'ArrowRight': skipForward(10); break;
    case 'ArrowUp': increaseSpeed(); break;
    case 'ArrowDown': decreaseSpeed(); break;
  }
});
```

## HTML Structure

### Transcript Segment
```html
<div class="transcript-segment" data-start="0.0" data-end="2.5">
  <span class="timestamp">[0:00]</span>
  <span class="text">Hello world this is a test</span>
</div>

<div class="transcript-segment active" data-start="2.5" data-end="5.0">
  <span class="timestamp">[0:03]</span>
  <span class="text">Another segment here that is currently playing</span>
</div>
```

### Audio Player
```html
<div class="player-container">
  <!-- Waveform or progress bar -->
  <div class="waveform">
    <div class="progress" style="width: 57%"></div>
  </div>

  <!-- Time display -->
  <div class="time-display">
    <span class="current-time">1:23</span>
    <span class="separator">/</span>
    <span class="total-time">2:25</span>
  </div>

  <!-- Controls -->
  <div class="player-controls">
    <button class="skip-backward">◀◀ 10s</button>
    <button class="play-pause">▶️</button>
    <button class="skip-forward">10s ▶▶</button>
    <input type="range" class="volume" min="0" max="100" value="100">
    <select class="speed">
      <option value="0.5">0.5x</option>
      <option value="1" selected>1x</option>
      <option value="1.5">1.5x</option>
      <option value="2">2x</option>
    </select>
    <button class="copy-transcript">📋 Copy</button>
  </div>

  <audio id="audioPlayer" preload="auto">
    <source src="/api/recordings/{id}/audio" type="audio/webm">
  </audio>
</div>
```

## CSS Highlights

```css
.transcript-segment {
  padding: 12px 16px;
  margin: 8px 0;
  border-radius: 8px;
  background: #f8f9fa;
  cursor: pointer;
  transition: all 0.2s ease;
}

.transcript-segment:hover {
  background: #e9ecef;
  transform: translateX(4px);
}

.transcript-segment.active {
  background: linear-gradient(135deg, #667eea33 0%, #764ba233 100%);
  font-weight: 600;
  border-left: 4px solid #667eea;
}

.timestamp {
  color: #667eea;
  font-weight: 600;
  margin-right: 8px;
  font-size: 0.9em;
}
```

## Multi-Chunk Handling

For recordings split into multiple chunks:
```javascript
// Load all chunks in sequence
const chunks = recording.chunks;
let currentChunkIndex = 0;

audioElement.addEventListener('ended', () => {
  if (currentChunkIndex < chunks.length - 1) {
    currentChunkIndex++;
    loadChunk(currentChunkIndex);
    audioElement.play();
  }
});

// Adjust timestamps to account for chunk offsets
function getGlobalTimestamp(chunkIndex, localTimestamp) {
  let offset = 0;
  for (let i = 0; i < chunkIndex; i++) {
    offset += chunks[i].duration;
  }
  return offset + localTimestamp;
}
```

## Optional: Waveform Visualization

Simple approach using Web Audio API:
```javascript
// Analyze audio and draw simple waveform bars
const audioContext = new AudioContext();
const analyser = audioContext.createAnalyser();
// Connect audio element to analyser
// Draw waveform to canvas
```

Or use existing library: **wavesurfer.js** (lightweight, vanilla JS)

## API Requirements

### GET `/api/recordings/<id>`
Returns complete metadata including all segments:
```json
{
  "id": "2025-10-27T14:30:45Z",
  "chunks": [
    {
      "segments": [
        {"start": 0.0, "end": 2.5, "text": "Hello world"},
        {"start": 2.5, "end": 5.0, "text": "Another segment"}
      ]
    }
  ]
}
```

### GET `/api/recordings/<id>/audio`
Serves merged audio or first chunk.

## Accessibility
- ARIA labels for all controls
- Keyboard navigation support
- Screen reader announcements for playback state
- Focus indicators on all interactive elements

## Testing
- Test with single-chunk recording
- Test with multi-chunk recording (3+ chunks)
- Test click-to-jump accuracy
- Test auto-highlight timing accuracy
- Test playback speed controls
- Test keyboard shortcuts
- Test copy transcript functionality
- Test on mobile devices (touch interactions)

## Future Enhancements (Optional)
- Waveform visualization with peaks
- Share recording (download audio + transcript)
- Edit transcript (fix transcription errors)
- Add notes/markers at specific timestamps
- Export transcript as PDF or TXT
