# Task 19: Optimize Transcription Latency (BACKLOG)

- [ ] Research real-time audio streaming options for faster-whisper
- [ ] Test reducing audio chunk duration from 3s to shorter intervals (e.g., 1s, 1.5s, 2s)
- [ ] Evaluate trade-offs between latency and transcription accuracy
- [ ] Implement optimal configuration based on testing results
- **Location:** `index.html` (audio chunking), `server.py` (streaming endpoint if needed)

## Context

Currently, the frontend sends audio chunks every 3 seconds to the backend for transcription. This creates a noticeable delay in the user experience.

## Options to Explore

### Option 1: Reduce Chunk Duration
- Simple change to `timeSlice` in MediaRecorder
- Test 1s, 1.5s, 2s intervals
- Measure impact on accuracy with shorter audio segments
- Quick win with minimal code changes

### Option 2: Real-time Audio Streaming
- Investigate if faster-whisper supports streaming transcription
- May require WebSocket connection instead of HTTP POST
- Could provide word-by-word transcription as user speaks
- More complex implementation but potentially much lower latency
- Research faster-whisper streaming capabilities and limitations

## Success Criteria
- Reduce perceived latency while maintaining transcription quality
- Document optimal configuration with test results
- Update code with best approach found
- No degradation in transcription accuracy

## Technical Considerations
- MediaRecorder API limitations with very short time slices
- faster-whisper model performance with shorter audio segments
- Network overhead vs. latency gains
- WebSocket implementation complexity if needed
