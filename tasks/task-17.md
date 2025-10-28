# Task 17: UI Polish and Refinements

- [x] Make orb 50% opaque when muted
- [x] Remove animating waveform when muted
- [x] Show microphone icon below waveform when active, make it smaller
- [x] Change "Muted" text to gray "You are muted"
- [x] Add copy icon to top right of transcription box
- [x] Add 3s delay to "No voice detected" message
- [x] Reduce transcription text size to match other UI text (0.95em)
- **Location:** `index.html`

## Context

Polish the UI with several refinements:
- Better visual feedback for muted state (opacity, no waveform)
- Improved microphone icon positioning (below waveform, smaller)
- More user-friendly muted message
- Copy functionality for transcription text
- Natural pause handling (3s delay before showing "No voice detected")

## Design Notes

- Muted state: 50% opacity on orb, hide waveform animation
- Microphone icon: Position below waveform bars, reduce size
- Status text: Gray color for "You are muted"
- Copy button: Top right corner of transcription box
- Voice detection: 3 second delay before showing message to account for natural speech pauses
