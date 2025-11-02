#!/usr/bin/env python3
"""Test script for /transcribe-file endpoint with SSE progress tracking"""

import requests
import json
import time

def test_transcribe_file(audio_file_path):
    url = 'http://localhost:10000/transcribe-file'

    print(f"Uploading file: {audio_file_path}")
    print("Starting transcription with streaming progress...\n")

    with open(audio_file_path, 'rb') as audio_file:
        files = {'audio': audio_file}

        response = requests.post(url, files=files, stream=True)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            return

        session_id = None
        segment_count = 0
        start_time = time.time()

        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    try:
                        data = json.loads(data_str)
                        msg_type = data.get('type')

                        if msg_type == 'started':
                            session_id = data['session_id']
                            print(f"✓ Session started: {session_id}")
                            print(f"  Total segments: {data['total_segments']}")
                            print(f"  Total duration: {data['total_duration']:.1f}s ({data['total_duration']/60:.1f} min)\n")

                        elif msg_type == 'progress':
                            segment = data['segment']
                            total = data['total_segments']
                            percent = data['percent']
                            remaining = data['estimated_remaining']
                            print(f"⏳ Progress: Segment {segment+1}/{total} ({percent}%) - Est. {remaining}s remaining")

                        elif msg_type == 'segment_complete':
                            segment_count += 1
                            segment_num = data['segment']
                            text = data['transcription'][:100]
                            print(f"✓ Segment {segment_num} complete: {text}...\n")

                        elif msg_type == 'complete':
                            elapsed = time.time() - start_time
                            print(f"\n🎉 Transcription complete!")
                            print(f"  Session ID: {data['session_id']}")
                            print(f"  Total duration: {data['total_duration']:.1f}s")
                            print(f"  Processing time: {elapsed:.1f}s")
                            print(f"  RTF: {elapsed/data['total_duration']:.2f}x")
                            print(f"  Segments processed: {segment_count}")
                            print(f"\nFiles saved:")
                            print(f"  - /tmp/whisper_sessions/{data['session_id']}/transcription.txt")
                            print(f"  - /tmp/whisper_sessions/{data['session_id']}/transcription.json")
                            print(f"\nDownload URLs:")
                            print(f"  Text: http://localhost:10000/download-transcription/{data['session_id']}")
                            print(f"  JSON: http://localhost:10000/download-transcription/{data['session_id']}/json")
                            print(f"\nStatus URL:")
                            print(f"  http://localhost:10000/transcribe-status/{data['session_id']}")

                        elif msg_type == 'error':
                            print(f"❌ Error: {data['message']}")

                    except json.JSONDecodeError as e:
                        print(f"Failed to parse: {data_str}")

if __name__ == '__main__':
    import sys

    audio_file = sys.argv[1] if len(sys.argv) > 1 else 'test-audio.mp3'
    test_transcribe_file(audio_file)
