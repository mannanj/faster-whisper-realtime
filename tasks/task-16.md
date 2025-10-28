# Task 16: Streamlined UI with Card Design and Click-to-Enable

- [x] Remove permission prompt screen
- [x] Make microphone button request permission on first click
- [x] Change orb color to green when recording (active state)
- [x] Put all UI elements in single white card container
- [x] Change transcription box to black background with white text
- **Location:** `index.html`

## Context

Simplified the UI flow by removing the separate permission prompt and making the microphone button handle permission requests on first click. Consolidated all UI elements into a single white card container for a cleaner, more cohesive design.

## Design Changes

- **Permission Flow**: Click microphone button to start (requests permission on first click)
- **Visual States**:
  - Inactive: Gray background (before first click)
  - Active/Recording: Green background (#4ade80)
  - Muted: Red background (#f5576c)
- **Layout**: All elements in single white card with rounded corners and shadow
- **Transcription Box**: Black background (#1a1a1a) with white monospace text for terminal-like appearance
- **Text Colors**: Updated metadata and status to dark colors for visibility on white card
