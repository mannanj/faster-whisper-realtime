# Task 29: LLM Integration for Transcript Correction

- [x] Add `anthropic` Python package to requirements.txt
- [x] Create `.env.local.example` with placeholder for ANTHROPIC_API_KEY
- [x] Add python-dotenv to requirements.txt for .env loading
- [x] Create LLM service module (`llm_service.py`) with Claude API integration
- [x] Design prompt that minimizes word changes while improving readability
- [x] Add error handling for API failures (graceful fallback to original transcript)
- [x] Test LLM correction with sample transcripts

**Location:** `requirements.txt`, `.env.local.example`, `llm_service.py`

## Context

This task sets up the infrastructure to use Anthropic's Claude Sonnet 4.5 to improve transcript readability while preserving most original words. The LLM will:

- Add proper punctuation (periods, commas, question marks)
- Fix capitalization (sentence starts, proper nouns)
- Add paragraph breaks between distinct topics/ideas
- **Minimize actual word changes** - only fix obvious speech-to-text errors
- Keep word order intact as much as possible

## Design Notes

### LLM Prompt Strategy
The prompt should be very explicit about constraints:
```
You are improving a speech-to-text transcript for readability.

CRITICAL RULES:
1. Keep 90%+ of the original words unchanged
2. Only fix obvious transcription errors
3. Preserve word order - do not rearrange
4. Add punctuation (periods, commas, question marks, etc.)
5. Fix capitalization (sentence starts, proper nouns)
6. Add paragraph breaks (use \n\n) between distinct topics/ideas
7. Remove filler words ONLY if excessive (um, uh, you know)

Original transcript:
{transcript}

Return ONLY the corrected transcript, no explanation.
```

### Error Handling
- If API fails, return original transcript unchanged
- If API key missing, log warning and return original transcript
- Timeout after 10 seconds

### Environment Variables
- `ANTHROPIC_API_KEY` - required for LLM calls
- Model: `claude-sonnet-4-5-20250929`
