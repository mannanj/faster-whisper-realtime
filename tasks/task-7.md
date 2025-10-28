# Task 7: Recordings Library UI

- [ ] Create `/recordings` route in Flask to serve library page
- [ ] Design recordings library HTML page with gradient theme
- [ ] Implement date-grouped list view for recordings
- [ ] Add search/filter functionality (by text or date)
- [ ] Display transcription preview, duration, language for each recording
- [ ] Add inline play/pause controls for each recording
- [ ] Implement delete recording functionality
- [ ] Add storage statistics dashboard (total recordings, duration, size)
- [ ] Create API endpoint GET `/api/recordings` to fetch recordings list
- [ ] Create API endpoint DELETE `/api/recordings/<id>` to delete recordings
- [ ] Add navigation link from main page to recordings library
- **Location:** `server.py` (new routes), new `recordings.html` file

## Purpose
Provide a beautiful, intuitive interface to browse, search, play, and manage all saved recordings with their transcriptions.

## UI Design (Minimal & Beautiful)

### Layout
```
┌─────────────────────────────────────────────────┐
│  🎙️ Recordings Library                          │
│  ← Back to Recorder                             │
│                                                  │
│  [Search recordings...        ] 🔍              │
│                                                  │
│  📊 Statistics                                   │
│  Total: 42 recordings • 3.2 hours • 156 MB      │
│                                                  │
│  📅 October 27, 2025                            │
│  ┌──────────────────────────────────────────┐  │
│  │ 🔊 14:30:45 • 2m 25s • English           │  │
│  │ "Hello world this is a test another..."  │  │
│  │ [▶ Play] [🗑️ Delete] [📝 View Full]     │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │ 🔊 10:15:22 • 45s • English              │  │
│  │ "Testing the transcription system..."    │  │
│  │ [▶ Play] [🗑️ Delete] [📝 View Full]     │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  📅 October 26, 2025                            │
│  ...                                             │
└─────────────────────────────────────────────────┘
```

### Style Guide
- Match existing gradient theme from index.html
- Same purple gradient background (`linear-gradient(135deg, #667eea 0%, #764ba2 100%)`)
- White container cards with rounded corners and shadows
- Smooth animations and transitions
- Responsive design for mobile/tablet

### Recording Card Design
```html
<div class="recording-card">
  <div class="recording-header">
    <span class="time">14:30:45</span>
    <span class="duration">2m 25s</span>
    <span class="language">English</span>
  </div>
  <div class="recording-preview">
    "Hello world this is a test another segment..."
  </div>
  <div class="recording-controls">
    <button class="play-btn">▶ Play</button>
    <button class="delete-btn">🗑️ Delete</button>
    <button class="view-btn">📝 View Full</button>
  </div>
  <audio class="recording-audio" src="/api/recordings/2025-10-27T14:30:45Z/audio"></audio>
</div>
```

## API Endpoints

### GET `/api/recordings`
```json
{
  "recordings": [
    {
      "id": "2025-10-27T14:30:45Z",
      "date": "2025-10-27",
      "time": "14:30:45",
      "duration": 145.2,
      "language": "en",
      "transcription_preview": "Hello world this is a test...",
      "chunks": 2,
      "compressed": false,
      "size": 1024000
    }
  ],
  "statistics": {
    "total_recordings": 42,
    "total_duration": 11520.5,
    "total_size": 6553600,
    "compressed_size": 1310720
  }
}
```

### GET `/api/recordings/<id>`
Returns full metadata JSON with all segments and chunks.

### GET `/api/recordings/<id>/audio`
Serves audio file (first chunk, or merged if needed).

### GET `/api/recordings/<id>/audio/chunk/<n>`
Serves specific chunk.

### DELETE `/api/recordings/<id>`
Deletes recording and all associated files (audio chunks, metadata JSON).

## Features

### Search/Filter
- Real-time text search through transcriptions
- Date range filtering
- Language filtering
- Duration filtering

### Inline Playback
- Click Play → audio plays inline in card
- Show playback progress bar
- Pause/resume controls
- Auto-scroll to playing recording

### Delete Confirmation
```javascript
// Simple confirmation dialog
if (confirm(`Delete recording from ${date} ${time}?\n\n"${preview}"\n\nThis cannot be undone.`)) {
  // Delete via API
}
```

### View Full Transcription
- Modal or expand card to show complete transcription
- Option to jump to detailed player view (Task 8)

## JavaScript Implementation (Vanilla)

```javascript
// Fetch recordings on page load
async function loadRecordings() {
  const response = await fetch('/api/recordings');
  const data = await response.json();
  renderRecordings(data.recordings);
  renderStatistics(data.statistics);
}

// Group by date and render
function renderRecordings(recordings) {
  const groupedByDate = groupByDate(recordings);
  // Render each date group
}

// Search functionality
searchInput.addEventListener('input', (e) => {
  const query = e.target.value.toLowerCase();
  // Filter and re-render recordings
});

// Play recording
function playRecording(id) {
  const audio = document.querySelector(`#recording-${id} audio`);
  audio.play();
  // Update UI to show playing state
}

// Delete recording
async function deleteRecording(id) {
  await fetch(`/api/recordings/${id}`, { method: 'DELETE' });
  // Remove from UI
  loadRecordings(); // Refresh
}
```

## Testing
- Test with no recordings (empty state)
- Test with 1-5 recordings
- Test with 50+ recordings (performance)
- Test search functionality
- Test play/pause controls
- Test delete functionality
- Test responsive design on mobile
