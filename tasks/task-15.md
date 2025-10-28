# Task 15: Vertical UI Layout Redesign

- [x] Reorganize main container to use vertical flexbox layout
- [x] First row: Microphone button centered
- [x] Second row: Language and duration info centered
- [x] Third row: Transcription text box (full width)
- [x] Adjust spacing and margins for vertical flow
- [x] Ensure responsive design on all screen sizes
- **Location:** `index.html`

## Context

Current UI has horizontal layout with mic button/info on left and text box on right. Need to convert to vertical stacked layout with three distinct rows:
1. Microphone button (centered)
2. Language/duration text (centered)
3. Transcription text box (full width below)

## Design Notes

- Use flexbox with `flex-direction: column`
- Center align first two rows
- Maintain existing visual styles (colors, gradients, animations)
- Keep transcription box styling but adjust width to 100%
- Adjust container max-width and padding as needed for vertical layout
