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
        Maps corrected words to original word timestamps using dynamic programming.

        Args:
            original_words: List of dicts with 'word', 'start', 'end', 'probability'
            corrected_text: Corrected transcript text

        Returns:
            List of dicts with corrected words and aligned timestamps
        """
        if not original_words:
            return []

        corrected_words = self.split_into_words(corrected_text)
        if not corrected_words:
            return []

        orig_normalized = [self.normalize_word(w['word']) for w in original_words]
        corr_normalized = [w['normalized'] for w in corrected_words]

        # Build alignment mapping using edit distance
        alignment = self._build_alignment(orig_normalized, corr_normalized)

        # Apply alignment to create timestamped words
        aligned_words = []
        for corr_idx, orig_idx in enumerate(alignment):
            corr_word = corrected_words[corr_idx]

            if orig_idx is not None:
                # Direct match - use original timestamp
                aligned_words.append({
                    'word': corr_word['word'],
                    'start': original_words[orig_idx]['start'],
                    'end': original_words[orig_idx]['end'],
                    'probability': original_words[orig_idx].get('probability', 0.0)
                })
            else:
                # Inserted word - interpolate timestamp
                start_time, end_time = self._interpolate_timestamp(
                    corr_idx, alignment, original_words
                )
                aligned_words.append({
                    'word': corr_word['word'],
                    'start': start_time,
                    'end': end_time,
                    'probability': 0.0
                })

        # Post-process to fix duplicate timestamps from Whisper
        aligned_words = self._fix_duplicate_timestamps(aligned_words)

        return aligned_words

    def _fix_duplicate_timestamps(self, words: List[Dict]) -> List[Dict]:
        """
        Fix words with same start/end timestamp (usually from Whisper edge cases).
        Gives them a small duration by interpolating between surrounding words.
        """
        MIN_DURATION = 0.1

        for i, word in enumerate(words):
            if word['start'] == word['end']:
                # Find surrounding timestamps
                prev_end = words[i-1]['end'] if i > 0 else None
                next_start = words[i+1]['start'] if i < len(words) - 1 else None

                # Adjust timestamp to give minimum duration
                if prev_end is not None and next_start is not None:
                    # Between two words
                    gap = next_start - prev_end
                    if gap >= MIN_DURATION:
                        # Enough space - center it
                        mid = (prev_end + next_start) / 2
                        word['start'] = mid - (MIN_DURATION / 2)
                        word['end'] = mid + (MIN_DURATION / 2)
                    elif gap > 0:
                        # Small gap - use what we have
                        word['start'] = prev_end
                        word['end'] = next_start
                    else:
                        # No gap (overlapping words) - create tiny duration
                        word['start'] = word['start']
                        word['end'] = word['start'] + 0.05
                elif prev_end is not None:
                    # After last word
                    word['start'] = prev_end
                    word['end'] = prev_end + MIN_DURATION
                elif next_start is not None:
                    # Before first word
                    word['start'] = max(0, next_start - MIN_DURATION)
                    word['end'] = next_start
                else:
                    # Single word (shouldn't happen)
                    word['end'] = word['start'] + MIN_DURATION

        return words

    def _build_alignment(
        self,
        orig_words: List[str],
        corr_words: List[str]
    ) -> List[Optional[int]]:
        """
        Build word alignment using edit distance.
        Returns a list where alignment[i] = j means corrected word i aligns to original word j,
        or None if it's an insertion.
        """
        n, m = len(orig_words), len(corr_words)

        # dp[i][j] = (cost, operation) for aligning orig[0:i] with corr[0:j]
        INF = float('inf')
        dp = [[(INF, None)] * (m + 1) for _ in range(n + 1)]
        dp[0][0] = (0, None)

        # Initialize: deleting original words (filler words removed)
        for i in range(1, n + 1):
            is_filler = orig_words[i-1] in ['um', 'uh', 'er', 'ah', 'like']
            cost = 0.1 if is_filler else 1.0
            dp[i][0] = (dp[i-1][0][0] + cost, ('del', i-1, None))

        # Initialize: inserting corrected words
        for j in range(1, m + 1):
            dp[0][j] = (dp[0][j-1][0] + 1.0, ('ins', None, j-1))

        # Fill DP table
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                orig_word = orig_words[i-1]
                corr_word = corr_words[j-1]

                # Match/substitution cost
                if orig_word == corr_word:
                    match_cost = 0
                elif not corr_word:  # Empty corrected word (punctuation only)
                    match_cost = 0.1
                else:
                    # Use similarity for substitution cost
                    similarity = self.calculate_similarity(orig_word, corr_word)
                    match_cost = 1.0 - similarity

                # Three operations: match/sub, delete, insert
                match = dp[i-1][j-1][0] + match_cost
                delete = dp[i-1][j][0] + (0.1 if orig_word in ['um', 'uh', 'er', 'ah'] else 1.0)
                insert = dp[i][j-1][0] + 1.0

                if match <= delete and match <= insert:
                    dp[i][j] = (match, ('match', i-1, j-1))
                elif delete <= insert:
                    dp[i][j] = (delete, ('del', i-1, j))
                else:
                    dp[i][j] = (insert, ('ins', i, j-1))

        # Backtrack to build alignment
        alignment = [None] * m
        i, j = n, m

        while i > 0 or j > 0:
            if dp[i][j][1] is None:
                break

            op, orig_idx, corr_idx = dp[i][j][1]

            if op == 'match':
                alignment[corr_idx] = orig_idx
                i, j = i - 1, j - 1
            elif op == 'del':
                i = i - 1
            elif op == 'ins':
                alignment[corr_idx] = None  # Inserted word
                j = j - 1

        return alignment

    def _interpolate_timestamp(
        self,
        corr_idx: int,
        alignment: List[Optional[int]],
        original_words: List[Dict]
    ) -> Tuple[float, float]:
        """
        Interpolate timestamp for an inserted word based on surrounding aligned words.
        """
        # Find previous aligned word
        prev_time = None
        for i in range(corr_idx - 1, -1, -1):
            if alignment[i] is not None:
                prev_time = original_words[alignment[i]]['end']
                break

        # Find next aligned word
        next_time = None
        for i in range(corr_idx + 1, len(alignment)):
            if alignment[i] is not None:
                next_time = original_words[alignment[i]]['start']
                break

        # Interpolate
        if prev_time is not None and next_time is not None:
            # Between two words - split the gap
            gap = next_time - prev_time
            if gap > 0.1:
                # Reasonable gap - interpolate in the middle
                mid_point = prev_time + (gap / 2)
                duration = min(gap / 2, 0.3)
                return mid_point - (duration / 2), mid_point + (duration / 2)
            else:
                # Very small or no gap - place at boundary with small duration
                return prev_time, prev_time + 0.15
        elif prev_time is not None:
            # After last aligned word
            return prev_time, prev_time + 0.3
        elif next_time is not None:
            # Before first aligned word
            return max(0, next_time - 0.3), next_time
        else:
            # No aligned words at all (shouldn't happen)
            return 0.0, 0.3

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
