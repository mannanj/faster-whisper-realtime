#!/usr/bin/env python3
"""
Test script to verify word alignment improvements.
"""

from llm_service import llm_service

def test_alignment():
    print("Testing Word Alignment Algorithm")
    print("=" * 60)

    # Test 1: Filler word removal
    print("\nTest 1: Filler word removal (um, uh)")
    original_words = [
        {'word': ' Hi', 'start': 0.0, 'end': 0.3, 'probability': 0.9},
        {'word': ' um', 'start': 0.3, 'end': 0.5, 'probability': 0.2},
        {'word': ' there', 'start': 0.5, 'end': 0.8, 'probability': 0.9},
    ]
    corrected = "Hi there"
    aligned = llm_service.align_words(original_words, corrected)
    print(f"  Original: {[w['word'] for w in original_words]}")
    print(f"  Corrected: {corrected}")
    print(f"  Result:")
    for w in aligned:
        print(f"    '{w['word']:10}' -> {w['start']:.2f}s to {w['end']:.2f}s")

    # Test 2: Word substitution
    print("\n\nTest 2: Word substitution (devor -> Devourer)")
    original_words = [
        {'word': ' the', 'start': 0.0, 'end': 0.2, 'probability': 0.9},
        {'word': ' devor', 'start': 0.2, 'end': 0.5, 'probability': 0.3},
        {'word': ' bling', 'start': 0.5, 'end': 0.8, 'probability': 0.4},
    ]
    corrected = "the Devourer Bling"
    aligned = llm_service.align_words(original_words, corrected)
    print(f"  Original: {[w['word'] for w in original_words]}")
    print(f"  Corrected: {corrected}")
    print(f"  Result:")
    for w in aligned:
        print(f"    '{w['word']:10}' -> {w['start']:.2f}s to {w['end']:.2f}s")

    # Test 3: Word insertion with interpolation
    print("\n\nTest 3: Word insertion (added 'really')")
    original_words = [
        {'word': ' This', 'start': 0.0, 'end': 0.3, 'probability': 0.9},
        {'word': ' is', 'start': 0.8, 'end': 1.0, 'probability': 0.9},
        {'word': ' good', 'start': 1.0, 'end': 1.3, 'probability': 0.9},
    ]
    corrected = "This is really good"
    aligned = llm_service.align_words(original_words, corrected)
    print(f"  Original: {[w['word'] for w in original_words]}")
    print(f"  Corrected: {corrected}")
    print(f"  Result:")
    for w in aligned:
        marker = " [INTERPOLATED]" if w['probability'] == 0.0 else ""
        print(f"    '{w['word']:10}' -> {w['start']:.2f}s to {w['end']:.2f}s{marker}")

    # Test 4: Check for same start/end bug
    print("\n\nTest 4: Verify no duplicate timestamps")
    has_duplicates = False
    for w in aligned:
        if w['start'] == w['end']:
            print(f"  ❌ ERROR: '{w['word']}' has same start/end: {w['start']:.2f}s")
            has_duplicates = True

    if not has_duplicates:
        print("  ✓ All words have distinct start/end timestamps")

    print("\n" + "=" * 60)
    print("Testing complete!")

if __name__ == '__main__':
    test_alignment()
