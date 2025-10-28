# Task 17: UI Polish and Refinements

- [x] Make orb 50% opaque when muted
- [x] Remove animating waveform when muted
- [x] Show microphone icon below waveform when active, make it smaller
- [x] Change "Muted" text to gray "You are muted"
- [x] Add copy icon to top right of transcription box
- [x] Add 3s delay to "No voice detected" message
- [x] Reduce transcription text size to match other UI text (0.95em)
- [x] Fix muted state: Show microphone and ball at 50% opacity with gray stroke and line through it
- [x] Make waveform bars twice as tall in fixed-height container
- [x] Reduce active microphone size to 1/3rd current size
- [x] Match microphone and waveform colors
- [x] Make inactive and muted microphone sizes identical (80px, centered)
- [x] Position active microphone below waveform inside circle
- [x] Hide waveform bars in inactive/muted states
- [x] Fix muted circle opacity to 50% using rgba without affecting icon opacity
- [x] Increase circle size by 50% (375px from 250px)
- **Location:** `index.html`

## Context

Polish the UI with several refinements:
- Better visual feedback for muted state (opacity, no waveform)
- Improved microphone icon positioning (below waveform, smaller)
- More user-friendly muted message
- Copy functionality for transcription text
- Natural pause handling (3s delay before showing "No voice detected")

**Bug Fixes:**
- Muted state should show microphone icon (not hide it)
- Microphone icon should be gray with line through it when muted
- Waveform bars should be twice as tall in fixed container
- Active microphone should be 1/3rd current size
- Microphone color should match waveform color
- Inactive and muted states should have identical microphone sizes (80px, centered)
- Active state should position microphone below waveform
- Circle opacity at 50% in muted state using rgba
- Circle size increased by 50% (375px)

## Design Notes

**Three States:**
- **Inactive state**: Large centered microphone (80px), gray color, no waveform
- **Muted state**: Large centered microphone (80px), gray with line through it, 50% opacity circle (rgba), no waveform
- **Active state**: Waveform bars twice as tall (300px max), small microphone (25px) below waveform, matching purple colors

- Fixed container heights prevent dynamic size changes during speech
- Status text: Gray color for "You are muted"
- Copy button: Top right corner of transcription box
- Voice detection: 3 second delay before showing message to account for natural speech pauses
