# Task 13: Always-On Ambient Transcription UI

- [ ] Auto-start recording on page load (after permission consent)
- [ ] Remove Start/Stop/Clear buttons from UI
- [ ] Replace UI with large centered microphone orb visualization
- [ ] Add animated waveform inside orb that responds to voice detection
- [ ] Display "No voice detected" message when silent
- [ ] Add pulsing glow effect behind orb when actively recording
- [ ] Implement mute toggle by clicking the orb
- [ ] Show line-through mic icon and grayscale/opacity change when muted
- [ ] Move language and duration info to subtle text below orb
- [ ] Remove "Powered by faster-whisper" branding
- [ ] Display transcription text in real-time as it streams
- **Location:** `index.html`

## Purpose
Transform the UI from a manual recording interface into an ambient, always-on transcription experience. The microphone starts automatically and continuously transcribes, with minimal UI controls—just a beautiful orb visualization that users can click to mute/unmute.

## Visual Design Specification

### Orb States

**Active Recording State:**
- Large white/theme-colored sphere in center of screen
- Animated waveform inside orb that moves with voice detection
- Pulsing green glow behind the orb (CSS box-shadow with animation)
- Clean microphone icon in center
- Text appears below in real-time as transcription streams

**Muted State:**
- Orb becomes grayscale/reduced opacity
- Line-through microphone icon (CSS or SVG)
- Red pulsing glow behind orb
- No waveform animation
- Transcription stops

**Silent (No Voice) State:**
- Active recording state visuals
- Display "No voice detected" message near orb
- Waveform becomes minimal/idle animation

### Layout

```
┌─────────────────────────────────┐
│                                 │
│                                 │
│          ╭─────────╮            │
│         │    🎤    │            │  ← Large orb with mic icon
│          ╰─────────╯            │     Pulsing green glow
│                                 │     Waveform animation inside
│     Language: en  •  4.56s      │  ← Subtle metadata
│     [No voice detected]         │  ← Status message
│                                 │
│  Transcribed text appears       │
│  here in real-time as the       │  ← Live transcription area
│  user speaks...                 │
│                                 │
└─────────────────────────────────┘
```

### Color Scheme

**Active/Recording:**
- Orb: White or theme accent color (current gradient colors)
- Glow: Green (#4ade80 or similar)
- Waveform: Animated gradient matching theme

**Muted:**
- Orb: Grayscale with 50% opacity
- Glow: Red (#f5576c)
- Icon: Gray with line-through

### Animation Specifications

**Pulsing Glow:**
```css
@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 20px 10px rgba(74, 222, 128, 0.3);
  }
  50% {
    box-shadow: 0 0 40px 20px rgba(74, 222, 128, 0.5);
  }
}
```

**Waveform:**
- Amplitude varies with audio input level (use Web Audio API AnalyserNode)
- Smooth easing between states
- Minimal baseline animation when no voice detected

**Mute Transition:**
- 300ms ease-in-out for opacity/grayscale
- Icon line-through fades in
- Glow color shifts from green to red

## Technical Implementation

### Auto-Start Flow

```javascript
async function initializeApp() {
  try {
    // Request mic permission
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    // Start recording immediately
    startRecording(stream);

    // Initialize waveform visualization
    initializeWaveform(stream);

    // Update UI to active state
    updateOrbState('active');

  } catch (error) {
    // Handle permission denied
    showPermissionError();
  }
}

// Call on page load
window.addEventListener('DOMContentLoaded', initializeApp);
```

### Waveform Visualization

Use Web Audio API to analyze audio and drive waveform animation:

```javascript
function initializeWaveform(stream) {
  const audioContext = new AudioContext();
  const analyser = audioContext.createAnalyser();
  const microphone = audioContext.createMediaStreamSource(stream);

  microphone.connect(analyser);
  analyser.fftSize = 256;

  const bufferLength = analyser.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);

  function updateWaveform() {
    requestAnimationFrame(updateWaveform);

    analyser.getByteFrequencyData(dataArray);

    // Calculate average amplitude
    const average = dataArray.reduce((a, b) => a + b) / bufferLength;

    // Update waveform visual
    updateWaveformBars(dataArray);

    // Show/hide "no voice" message
    if (average < VOICE_THRESHOLD) {
      showNoVoiceMessage();
    } else {
      hideNoVoiceMessage();
    }
  }

  updateWaveform();
}
```

### Mute Toggle

```javascript
let isMuted = false;
let mediaRecorder;

function toggleMute() {
  isMuted = !isMuted;

  if (isMuted) {
    // Stop transcription stream
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
    }

    // Update orb to muted state
    updateOrbState('muted');

  } else {
    // Resume recording
    startRecording();

    // Update orb to active state
    updateOrbState('active');
  }
}

// Add click listener to orb
document.querySelector('.orb').addEventListener('click', toggleMute);
```

### Metadata Display

```javascript
function updateMetadata(language, duration) {
  const metadataEl = document.querySelector('.metadata');
  metadataEl.textContent = `Language: ${language} • ${duration.toFixed(2)}s`;
}

// Update during SSE stream
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'metadata') {
    updateMetadata(data.language, data.duration);
  }

  if (data.type === 'segment') {
    appendTranscription(data.text);
  }
};
```

## UI Component Structure

```html
<div class="app-container">
  <!-- Orb visualization -->
  <div class="orb-container">
    <div class="orb" data-state="active">
      <div class="glow"></div>
      <div class="waveform-container">
        <!-- SVG or canvas waveform -->
      </div>
      <svg class="mic-icon">
        <!-- Microphone icon with optional line-through -->
      </svg>
    </div>
  </div>

  <!-- Subtle metadata -->
  <div class="metadata">
    Language: en • 4.56s
  </div>

  <!-- Status message -->
  <div class="status-message">
    No voice detected
  </div>

  <!-- Live transcription -->
  <div class="transcription">
    <!-- Text streams here -->
  </div>
</div>
```

## CSS Guidelines

- Use CSS custom properties for theme colors
- Orb size: 200-300px diameter
- Responsive: scale down on mobile
- Smooth transitions for all state changes
- Use backdrop-filter for subtle blur effects if desired
- Maintain gradient background from current design

## User Experience Flow

1. **Page loads** → "Allow microphone access?" browser prompt appears
2. **User grants permission** → Orb appears with green pulsing glow, starts recording
3. **User speaks** → Waveform animates, text appears below in real-time
4. **Silence detected** → "No voice detected" message shows
5. **User clicks orb** → Mutes (red glow, grayscale, line-through icon)
6. **User clicks again** → Unmutes (returns to active state)

## Accessibility Considerations

- Add ARIA labels to orb ("Microphone active, click to mute")
- Keyboard support: Space/Enter to toggle mute
- Screen reader announcements for state changes
- Ensure text contrast meets WCAG standards
- Alt text for visual indicators

## Browser Compatibility

- MediaRecorder API (already in use)
- Web Audio API for waveform (AnalyserNode)
- CSS backdrop-filter (optional, progressive enhancement)
- All modern browsers (Chrome, Firefox, Safari, Edge)

## Testing Checklist

- [ ] Auto-start works after permission grant
- [ ] Waveform animates with voice
- [ ] "No voice detected" appears during silence
- [ ] Orb click toggles mute/unmute
- [ ] Visual states match specification (colors, opacity, glow)
- [ ] Metadata displays correctly below orb
- [ ] Transcription continues to stream in real-time
- [ ] Keyboard navigation works (Tab to orb, Space to toggle)
- [ ] Responsive on mobile devices
- [ ] Permission denied shows appropriate error message

## Dependencies

No new dependencies required. Uses existing:
- MediaRecorder API (audio capture)
- Web Audio API (waveform visualization)
- Fetch API or WebSocket (transcription streaming from Task 12)

## Rollback Plan

If always-on UX proves problematic (privacy concerns, performance):
- Add simple toggle button near orb to enable/disable auto-start
- Keep manual Start button as fallback option
- Store preference in localStorage

## Future Enhancements

- **Voice Activity Detection (VAD):** More accurate "no voice" detection
- **Multiple orb themes:** User-selectable color schemes
- **Waveform styles:** Different visualization options (bars, circle, line)
- **Gesture controls:** Swipe to mute, hold to pause, etc.
- **Mini mode:** Floating orb that can be minimized to corner
