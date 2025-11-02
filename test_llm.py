#!/usr/bin/env python3
"""Test script for LLM transcript correction"""

from llm_service import llm_service

# Sample transcript with typical speech-to-text issues
test_transcript = "um so i think we should like you know go to the store today and get some groceries we need milk bread eggs and stuff"

test_words = [
    {"word": " um", "start": 0.0, "end": 0.2, "probability": 0.8},
    {"word": " so", "start": 0.2, "end": 0.4, "probability": 0.9},
    {"word": " i", "start": 0.5, "end": 0.6, "probability": 0.95},
    {"word": " think", "start": 0.7, "end": 0.9, "probability": 0.92},
    {"word": " we", "start": 1.0, "end": 1.1, "probability": 0.94},
    {"word": " should", "start": 1.2, "end": 1.5, "probability": 0.93},
    {"word": " like", "start": 1.6, "end": 1.8, "probability": 0.85},
    {"word": " you", "start": 1.9, "end": 2.0, "probability": 0.88},
    {"word": " know", "start": 2.1, "end": 2.3, "probability": 0.87},
    {"word": " go", "start": 2.4, "end": 2.6, "probability": 0.91},
    {"word": " to", "start": 2.7, "end": 2.8, "probability": 0.95},
    {"word": " the", "start": 2.9, "end": 3.0, "probability": 0.96},
    {"word": " store", "start": 3.1, "end": 3.4, "probability": 0.93},
    {"word": " today", "start": 3.5, "end": 3.9, "probability": 0.92},
]

print("Testing LLM Service")
print("=" * 60)
print(f"\nOriginal transcript:\n{test_transcript}\n")

corrected_text, aligned_words = llm_service.correct_and_align(
    test_transcript,
    test_words
)

print(f"Corrected transcript:\n{corrected_text}\n")
print(f"Aligned words ({len(aligned_words)} words):")
for i, word in enumerate(aligned_words[:10]):  # Show first 10
    print(f"  {i+1}. '{word['word']}' @ {word['start']:.2f}s - {word['end']:.2f}s")

if len(aligned_words) > 10:
    print(f"  ... and {len(aligned_words) - 10} more words")

print("\n" + "=" * 60)
print("✅ Test complete!")
