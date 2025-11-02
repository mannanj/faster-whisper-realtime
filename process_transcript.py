#!/usr/bin/env python3
"""Process a saved transcript with LLM correction and word alignment"""

import json
import sys
from pathlib import Path
from llm_service import llm_service

def process_session(session_id: str):
    """Process a session's transcript with LLM correction"""

    session_dir = Path('data/sessions') / session_id
    transcript_file = session_dir / 'transcription.json'

    if not transcript_file.exists():
        print(f"Error: Transcript file not found at {transcript_file}")
        return False

    print(f"Loading transcript from {transcript_file}...")
    with open(transcript_file, 'r') as f:
        data = json.load(f)

    print(f"Original transcript length: {len(data['full_transcription'])} chars")
    print(f"Number of segments: {len(data['segments'])}")

    # Process each segment
    print("\nProcessing segments with LLM...")
    for i, segment in enumerate(data['segments']):
        print(f"  Segment {i+1}/{len(data['segments'])}...", end=' ')

        original_text = segment['transcription']
        original_words = segment.get('words', [])

        # Correct and align words
        corrected_text, aligned_words = llm_service.correct_and_align(
            original_text,
            original_words
        )

        # Update segment with corrected data
        segment['transcription_corrected'] = corrected_text
        segment['words_corrected'] = aligned_words

        print(f"✓ ({len(corrected_text)} chars, {len(aligned_words)} words)")

    # Rebuild full corrected transcript from segments
    full_corrected = ' '.join(
        segment['transcription_corrected']
        for segment in data['segments']
    )
    data['full_transcription_corrected'] = full_corrected

    print(f"\nCorrected transcript length: {len(full_corrected)} chars")

    # Save updated transcript
    print(f"\nSaving corrected transcript to {transcript_file}...")
    with open(transcript_file, 'w') as f:
        json.dump(data, f, indent=2)

    print("✅ Done!")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 process_transcript.py <session_id>")
        print("\nExample:")
        print("  python3 process_transcript.py 8e3aa0f8-93fc-4a04-a082-84675272acb1")
        sys.exit(1)

    session_id = sys.argv[1]
    success = process_session(session_id)
    sys.exit(0 if success else 1)
