# Task 18: LLM-Powered Transcription Formatting and Refinement (BACKLOG)

- [ ] Process larger chunks with LLM for improved accuracy
- [ ] Implement final session-wide accuracy pass
- [ ] Return multiple transcription assessments with confidence scores
- [ ] Design UI for showing multiple possible transcription versions
- [ ] Allow user to pick/select between different transcription assessments
- [ ] Add manual editing capability for transcriptions
- [ ] Implement grammar correction
- [ ] Add logical line breaking and text formatting
- [ ] Create UI for editing/adjusting transcriptions
- **Location:** `server.py`, `index.html`

## Context

Enhance transcription accuracy and formatting using LLM post-processing:

### Backend Processing Goals:
1. **Multi-Pass Accuracy**:
   - Process larger chunks for better context
   - Final session-wide pass for overall coherence
   - Multiple assessment generation with confidence scores

2. **LLM Features**:
   - Grammar correction
   - Punctuation refinement
   - Logical paragraph/line breaking
   - Sentence restructuring for clarity

### Frontend Features:
1. **Multiple Versions UI**:
   - Display different transcription assessments
   - Show confidence scores
   - Allow user selection between versions

2. **Manual Editing**:
   - Make transcription text editable
   - Real-time editing capability
   - Save/update edited versions

3. **Formatting Display**:
   - Proper line breaks for logical flow
   - Formatted text with proper paragraphs
   - Grammar-corrected output

## Technical Considerations

- LLM choice (GPT-4, Claude, local model)
- API integration for post-processing
- State management for multiple versions
- UI/UX for version comparison and selection
- Edit history tracking
- Performance implications of multi-pass processing

## Design Questions to Resolve

- How to visually distinguish between multiple versions?
- Should we show confidence scores inline or in a separate panel?
- How to handle real-time editing vs. LLM suggestions?
- Should we allow toggling between raw and formatted versions?
- What LLM model provides best accuracy/speed trade-off?
