#!/usr/bin/env python3
import os
import tempfile
import json
import time
import uuid
import shutil
import subprocess
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context, send_file
from flask_cors import CORS
from faster_whisper import WhisperModel

app = Flask(__name__, static_folder='.')
CORS(app)

if 'OMP_NUM_THREADS' not in os.environ:
    import multiprocessing
    num_cores = multiprocessing.cpu_count()
    os.environ['OMP_NUM_THREADS'] = str(num_cores)
    print(f"Setting OMP_NUM_THREADS to {num_cores} (detected CPU cores)")

print("Loading Whisper model...")
model = WhisperModel("base", device="cpu", compute_type="int8")
print("Model loaded successfully!")

SESSIONS_DIR = Path(tempfile.gettempdir()) / "whisper_sessions"
SESSIONS_DIR.mkdir(exist_ok=True)
SESSION_TIMEOUT = 3600

def get_audio_duration(audio_path):
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())

def split_audio_into_segments(audio_path, session_dir, segment_duration_seconds=300):
    total_duration = get_audio_duration(audio_path)
    segments = []
    segment_index = 0

    current_time = 0.0
    while current_time < total_duration:
        segment_path = session_dir / f"segment_{segment_index}.mp3"
        end_time = min(current_time + segment_duration_seconds, total_duration)
        duration = end_time - current_time

        cmd = [
            'ffmpeg', '-i', audio_path, '-ss', str(current_time),
            '-t', str(duration), '-acodec', 'libmp3lame', '-y',
            str(segment_path)
        ]
        subprocess.run(cmd, capture_output=True)

        segments.append({
            'index': segment_index,
            'start_time': current_time,
            'end_time': end_time,
            'path': segment_path
        })

        current_time = end_time
        segment_index += 1

    return segments, total_duration

def cleanup_old_sessions():
    current_time = time.time()
    for session_dir in SESSIONS_DIR.iterdir():
        if session_dir.is_dir():
            dir_age = current_time - session_dir.stat().st_mtime
            if dir_age > SESSION_TIMEOUT:
                shutil.rmtree(session_dir)
                print(f"Cleaned up old session: {session_dir.name}")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/transcribe-file', methods=['POST'])
def transcribe_file():
    cleanup_old_sessions()

    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    session_id = str(uuid.uuid4())
    session_dir = SESSIONS_DIR / session_id
    session_dir.mkdir(exist_ok=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_audio:
        audio_file.save(temp_audio.name)
        temp_path = temp_audio.name

    try:
        print(f"Processing file for session {session_id}")
        audio_segments, total_duration = split_audio_into_segments(temp_path, session_dir)
        print(f"Split audio into {len(audio_segments)} segments (total duration: {total_duration:.2f}s)")

        results = []
        for segment_info in audio_segments:
            idx = segment_info['index']
            segment_path = segment_info['path']

            print(f"Transcribing segment {idx}...")
            start_time = time.time()
            segments, info = model.transcribe(str(segment_path), beam_size=1, vad_filter=True)

            transcription_parts = []
            for seg in segments:
                transcription_parts.append(seg.text)

            transcription_text = " ".join(transcription_parts).strip()
            transcription_time = time.time() - start_time
            segment_duration = segment_info['end_time'] - segment_info['start_time']
            rtf = transcription_time / segment_duration if segment_duration > 0 else 0

            print(f"[Performance] Segment {idx}: {segment_duration:.2f}s audio in {transcription_time:.2f}s (RTF: {rtf:.2f}x)")

            results.append({
                'index': idx,
                'start_time': segment_info['start_time'],
                'end_time': segment_info['end_time'],
                'transcription': transcription_text,
                'audio_url': f'/audio-segment/{session_id}/{idx}',
                'language': info.language if idx == 0 else results[0]['language']
            })

        return jsonify({
            'session_id': session_id,
            'total_duration': total_duration,
            'segments': results
        })

    except Exception as e:
        if session_dir.exists():
            shutil.rmtree(session_dir)
        return jsonify({'error': str(e)}), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/audio-segment/<session_id>/<int:segment_index>')
def serve_audio_segment(session_id, segment_index):
    segment_path = SESSIONS_DIR / session_id / f"segment_{segment_index}.mp3"

    if not segment_path.exists():
        return jsonify({'error': 'Segment not found'}), 404

    return send_file(segment_path, mimetype='audio/mpeg')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']

    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
        audio_file.save(temp_audio.name)
        temp_path = temp_audio.name

    def generate_segments():
        try:
            start_time = time.time()
            segments, info = model.transcribe(temp_path, beam_size=1, vad_filter=True)

            yield f"data: {json.dumps({'type': 'metadata', 'language': info.language, 'duration': info.duration})}\n\n"

            for segment in segments:
                yield f"data: {json.dumps({'type': 'segment', 'start': segment.start, 'end': segment.end, 'text': segment.text})}\n\n"

            transcription_time = time.time() - start_time
            rtf = transcription_time / info.duration if info.duration > 0 else 0
            print(f"[Performance] Transcribed {info.duration:.2f}s audio in {transcription_time:.2f}s (RTF: {rtf:.2f}x)")

            yield f"data: {json.dumps({'type': 'complete'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    return Response(stream_with_context(generate_segments()), mimetype='text/event-stream')

@app.route('/transcribe-live', methods=['POST'])
def transcribe_live():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio chunk provided'}), 400

    audio_chunk = request.files['audio']
    chunk_index = request.form.get('chunk_index', 0)
    session_id = request.form.get('session_id', 'default')

    print(f"\n[Server] Received chunk {chunk_index} for session {session_id}")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
        audio_chunk.save(temp_audio.name)
        chunk_size = os.path.getsize(temp_audio.name)
        temp_path = temp_audio.name
        print(f"[Server] Chunk {chunk_index} size: {chunk_size} bytes, saved to {temp_path}")

    def generate_segments():
        try:
            start_time = time.time()
            print(f"[Server] Starting transcription for chunk {chunk_index}...")
            segments, info = model.transcribe(temp_path, beam_size=1, vad_filter=True)

            if int(chunk_index) == 0:
                print(f"[Server] Chunk {chunk_index} metadata: language={info.language}")
                yield f"data: {json.dumps({'type': 'metadata', 'language': info.language})}\n\n"

            segment_count = 0
            for segment in segments:
                segment_count += 1
                print(f"[Server] Chunk {chunk_index} segment {segment_count}: '{segment.text}'")
                yield f"data: {json.dumps({'type': 'segment', 'start': segment.start, 'end': segment.end, 'text': segment.text})}\n\n"

            transcription_time = time.time() - start_time
            audio_duration = info.duration if hasattr(info, 'duration') else 3.0
            rtf = transcription_time / audio_duration if audio_duration > 0 else 0
            print(f"[Performance] Chunk {chunk_index}: {audio_duration:.2f}s audio in {transcription_time:.2f}s (RTF: {rtf:.2f}x, {segment_count} segments)")

            print(f"[Server] Chunk {chunk_index} complete ({segment_count} segments)")
            yield f"data: {json.dumps({'type': 'chunk_complete', 'chunk_index': chunk_index})}\n\n"

        except Exception as e:
            print(f"[Server] Error transcribing chunk {chunk_index}: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"[Server] Cleaned up temp file for chunk {chunk_index}")

    return Response(stream_with_context(generate_segments()), mimetype='text/event-stream')

if __name__ == '__main__':
    print("\n🎙️  Faster Whisper Real-time Transcription Server")
    print("=" * 50)
    print("Server starting on http://localhost:10000")
    print("Open your browser and start speaking!\n")
    app.run(debug=True, host='0.0.0.0', port=10000, use_reloader=False)
