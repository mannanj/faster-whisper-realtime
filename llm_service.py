#!/usr/bin/env python3
import os
import re
from typing import List, Dict, Optional, Tuple
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv('.env.local')

class LLMService:
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.client = None
        self.model = "claude-sonnet-4-5-20250929"

        if self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
                print("LLM Service initialized successfully")
            except Exception as e:
                print(f"Warning: Could not initialize Anthropic client: {e}")
                self.client = None
        else:
            print("Warning: ANTHROPIC_API_KEY not found in .env.local - LLM correction disabled")

    def correct_transcript(self, transcript: str) -> str:
        """
        Improves transcript readability while minimizing word changes.
        Returns corrected transcript or original if API fails.
        """
        if not self.client or not transcript.strip():
            return transcript

        prompt = f"""You are improving a speech-to-text transcript for readability.

CRITICAL RULES:
1. Keep 90%+ of the original words unchanged
2. Only fix obvious transcription errors (e.g., "there" → "their" when contextually wrong)
3. Preserve word order - do not rearrange sentences
4. Add punctuation (periods, commas, question marks, exclamation points)
5. Fix capitalization (sentence starts, proper nouns like names, places, brands)
6. Add paragraph breaks (use double newlines) between distinct topics or ideas
7. Remove filler words ONLY if excessive (um, uh, you know, like)
8. Maintain natural speech patterns - don't make it overly formal

Original transcript:
{transcript}

Return ONLY the corrected transcript with no explanation, commentary, or markdown formatting."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            corrected = response.content[0].text.strip()

            if not corrected:
                print("Warning: LLM returned empty response, using original transcript")
                return transcript

            return corrected

        except Exception as e:
            print(f"Error during LLM correction: {e}")
            return transcript

    def normalize_word(self, word: str) -> str:
        """Normalize word for comparison by removing punctuation and lowercasing."""
        return re.sub(r'[^\w\s]', '', word.lower())

    def split_into_words(self, text: str) -> List[Dict[str, str]]:
        """
        Splits text into words while preserving punctuation attachment.
        Returns list of dicts with 'word' (with punctuation) and 'normalized' keys.
        """
        words = []
        tokens = re.findall(r'\S+', text)

        for token in tokens:
            words.append({
                'word': token,
                'normalized': self.normalize_word(token)
            })

        return words

    def calculate_similarity(self, word1: str, word2: str) -> float:
        """Simple similarity score based on character overlap."""
        if word1 == word2:
            return 1.0

        set1 = set(word1.lower())
        set2 = set(word2.lower())

        if not set1 or not set2:
            return 0.0

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0

    def align_words(
        self,
        original_words: List[Dict],
        corrected_text: str
    ) -> List[Dict]:
        """
        Maps corrected words to original word timestamps.

        Args:
            original_words: List of dicts with 'word', 'start', 'end', 'probability'
            corrected_text: Corrected transcript text

        Returns:
            List of dicts with corrected words and aligned timestamps
        """
        if not original_words:
            return []

        corrected_words = self.split_into_words(corrected_text)
        aligned_words = []

        orig_idx = 0
        corr_idx = 0

        while corr_idx < len(corrected_words) and orig_idx < len(original_words):
            corr_word = corrected_words[corr_idx]
            orig_word = original_words[orig_idx]

            corr_normalized = corr_word['normalized']
            orig_normalized = self.normalize_word(orig_word['word'])

            if corr_normalized == orig_normalized:
                aligned_words.append({
                    'word': corr_word['word'],
                    'start': orig_word['start'],
                    'end': orig_word['end'],
                    'probability': orig_word.get('probability', 0.0)
                })
                corr_idx += 1
                orig_idx += 1

            elif not corr_normalized:
                corr_idx += 1

            elif not orig_normalized or orig_normalized in ['um', 'uh', 'er', 'ah', 'like', 'you', 'know']:
                if orig_idx + 1 < len(original_words):
                    next_orig_normalized = self.normalize_word(original_words[orig_idx + 1]['word'])
                    if corr_normalized == next_orig_normalized:
                        orig_idx += 1
                        continue
                orig_idx += 1

            else:
                best_match_offset = 0
                best_similarity = self.calculate_similarity(corr_normalized, orig_normalized)

                for offset in range(1, min(3, len(original_words) - orig_idx)):
                    candidate = self.normalize_word(original_words[orig_idx + offset]['word'])
                    similarity = self.calculate_similarity(corr_normalized, candidate)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match_offset = offset

                if best_match_offset > 0:
                    orig_idx += best_match_offset
                    continue

                aligned_words.append({
                    'word': corr_word['word'],
                    'start': orig_word['start'],
                    'end': orig_word['end'],
                    'probability': orig_word.get('probability', 0.0)
                })
                corr_idx += 1
                orig_idx += 1

        while corr_idx < len(corrected_words):
            if orig_idx > 0:
                last_word = original_words[orig_idx - 1]
                aligned_words.append({
                    'word': corrected_words[corr_idx]['word'],
                    'start': last_word['end'],
                    'end': last_word['end'] + 0.5,
                    'probability': 0.0
                })
            corr_idx += 1

        return aligned_words

    def correct_and_align(
        self,
        original_text: str,
        original_words: List[Dict]
    ) -> Tuple[str, List[Dict]]:
        """
        Corrects transcript and aligns words to preserve timestamps.

        Args:
            original_text: Original raw transcript
            original_words: List of word dicts with timestamps

        Returns:
            Tuple of (corrected_text, aligned_words)
        """
        corrected_text = self.correct_transcript(original_text)

        if not original_words:
            return corrected_text, []

        aligned_words = self.align_words(original_words, corrected_text)

        return corrected_text, aligned_words

llm_service = LLMService()
