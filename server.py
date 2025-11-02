#!/usr/bin/env python3
import os
import json
import time
import uuid
import shutil
import subprocess
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context, send_file
from flask_cors import CORS
from faster_whisper import WhisperModel
from llm_service import llm_service

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

SESSIONS_DIR = Path(__file__).parent / "data" / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

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

def update_session_status(session_dir, status_data):
    status_file = session_dir / 'status.json'
    with open(status_file, 'w') as f:
        json.dump(status_data, f, indent=2)

def get_session_status(session_dir):
    status_file = session_dir / 'status.json'
    if not status_file.exists():
        return None
    with open(status_file, 'r') as f:
        return json.load(f)

def save_transcription_files(session_dir, segments_data, total_duration):
    full_text = " ".join([seg['transcription'] for seg in segments_data]).strip()

    txt_file = session_dir / 'transcription.txt'
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(full_text)

    json_file = session_dir / 'transcription.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_duration': total_duration,
            'full_transcription': full_text,
            'segments': segments_data
        }, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/transcribe-file', methods=['POST'])
def transcribe_file():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    word_timestamps = request.form.get('word_timestamps', 'false').lower() == 'true'
    session_id = str(uuid.uuid4())
    session_dir = SESSIONS_DIR / session_id
    session_dir.mkdir(exist_ok=True)

    audio_path = session_dir / 'original_audio.webm'
    audio_file.save(str(audio_path))
    temp_path = str(audio_path)

    def generate_progress():
        try:
            print(f"Processing file for session {session_id}")

            update_session_status(session_dir, {
                'status': 'splitting',
                'session_id': session_id,
                'started_at': time.time()
            })

            audio_segments, total_duration = split_audio_into_segments(temp_path, session_dir)
            total_segments = len(audio_segments)
            print(f"Split audio into {total_segments} segments (total duration: {total_duration:.2f}s)")

            yield f"data: {json.dumps({'type': 'started', 'session_id': session_id, 'total_segments': total_segments, 'total_duration': total_duration})}\n\n"

            update_session_status(session_dir, {
                'status': 'processing',
                'session_id': session_id,
                'total_segments': total_segments,
                'current_segment': 0,
                'total_duration': total_duration,
                'started_at': time.time()
            })

            results = []
            avg_rtf = 0.25

            for segment_info in audio_segments:
                idx = segment_info['index']
                segment_path = segment_info['path']
                segment_duration = segment_info['end_time'] - segment_info['start_time']

                segments_remaining = total_segments - idx
                estimated_remaining = int(segments_remaining * segment_duration * avg_rtf)
                percent_complete = int((idx / total_segments) * 100)

                update_session_status(session_dir, {
                    'status': 'processing',
                    'session_id': session_id,
                    'total_segments': total_segments,
                    'current_segment': idx,
                    'percent_complete': percent_complete,
                    'estimated_seconds_remaining': estimated_remaining,
                    'total_duration': total_duration
                })

                yield f"data: {json.dumps({'type': 'progress', 'segment': idx, 'total_segments': total_segments, 'percent': percent_complete, 'estimated_remaining': estimated_remaining})}\n\n"

                print(f"Transcribing segment {idx}...")
                start_time = time.time()
                segments, info = model.transcribe(str(segment_path), beam_size=1, vad_filter=True, word_timestamps=word_timestamps)

                transcription_parts = []
                all_words = []
                for seg in segments:
                    transcription_parts.append(seg.text)
                    if word_timestamps and hasattr(seg, 'words') and seg.words:
                        for word in seg.words:
                            all_words.append({
                                'word': word.word,
                                'start': word.start,
                                'end': word.end,
                                'probability': word.probability
                            })

                transcription_text = " ".join(transcription_parts).strip()
                transcription_time = time.time() - start_time
                rtf = transcription_time / segment_duration if segment_duration > 0 else 0
                avg_rtf = (avg_rtf * idx + rtf) / (idx + 1)

                print(f"[Performance] Segment {idx}: {segment_duration:.2f}s audio in {transcription_time:.2f}s (RTF: {rtf:.2f}x)")

                segment_result = {
                    'index': idx,
                    'start_time': segment_info['start_time'],
                    'end_time': segment_info['end_time'],
                    'transcription': transcription_text,
                    'audio_url': f'/audio-segment/{session_id}/{idx}',
                    'language': info.language if idx == 0 else results[0]['language'],
                    'words': all_words if all_words else []
                }
                if word_timestamps and all_words:
                    corrected_text, aligned_words = llm_service.correct_and_align(
                        transcription_text,
                        all_words
                    )
                    segment_result['transcription_corrected'] = corrected_text
                    segment_result['words_corrected'] = aligned_words
                results.append(segment_result)

                yield f"data: {json.dumps({'type': 'segment_complete', 'segment': idx, 'transcription': transcription_text, 'start_time': segment_info['start_time'], 'end_time': segment_info['end_time']})}\n\n"

            save_transcription_files(session_dir, results, total_duration)

            update_session_status(session_dir, {
                'status': 'complete',
                'session_id': session_id,
                'total_segments': total_segments,
                'percent_complete': 100,
                'total_duration': total_duration,
                'completed_at': time.time()
            })

            yield f"data: {json.dumps({'type': 'complete', 'session_id': session_id, 'total_duration': total_duration, 'segments': results})}\n\n"

        except Exception as e:
            print(f"Error processing file: {e}")
            update_session_status(session_dir, {
                'status': 'error',
                'error': str(e)
            })
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return Response(stream_with_context(generate_progress()), mimetype='text/event-stream')

@app.route('/audio-segment/<session_id>/<int:segment_index>')
def serve_audio_segment(session_id, segment_index):
    segment_path = SESSIONS_DIR / session_id / f"segment_{segment_index}.mp3"

    if not segment_path.exists():
        return jsonify({'error': 'Segment not found'}), 404

    return send_file(segment_path, mimetype='audio/mpeg')

@app.route('/transcribe-status/<session_id>')
def get_transcribe_status(session_id):
    session_dir = SESSIONS_DIR / session_id

    if not session_dir.exists():
        return jsonify({'error': 'Session not found'}), 404

    status = get_session_status(session_dir)
    if status is None:
        return jsonify({'error': 'No status available'}), 404

    return jsonify(status)

@app.route('/download-transcription/<session_id>')
@app.route('/download-transcription/<session_id>/<format>')
def download_transcription(session_id, format='txt'):
    session_dir = SESSIONS_DIR / session_id

    if not session_dir.exists():
        return jsonify({'error': 'Session not found'}), 404

    if format == 'json':
        file_path = session_dir / 'transcription.json'
        mimetype = 'application/json'
        download_name = f'transcription_{session_id}.json'
    else:
        file_path = session_dir / 'transcription.txt'
        mimetype = 'text/plain'
        download_name = f'transcription_{session_id}.txt'

    if not file_path.exists():
        return jsonify({'error': 'Transcription not found. Processing may not be complete.'}), 404

    return send_file(file_path, mimetype=mimetype, as_attachment=True, download_name=download_name)

@app.route('/sessions')
def list_sessions():
    sessions = []

    for session_dir in SESSIONS_DIR.iterdir():
        if not session_dir.is_dir():
            continue

        status_file = session_dir / 'status.json'
        if not status_file.exists():
            continue

        try:
            with open(status_file, 'r') as f:
                status_data = json.load(f)

            session_info = {
                'session_id': session_dir.name,
                'status': status_data.get('status', 'unknown'),
                'total_duration': status_data.get('total_duration', 0),
                'total_segments': status_data.get('total_segments', 0),
                'created_at': status_data.get('started_at', session_dir.stat().st_ctime),
                'completed_at': status_data.get('completed_at')
            }
            sessions.append(session_info)
        except Exception as e:
            print(f"Error reading session {session_dir.name}: {e}")
            continue

    sessions.sort(key=lambda x: x['created_at'], reverse=True)
    return jsonify(sessions)

@app.route('/session/<session_id>')
def get_session(session_id):
    session_dir = SESSIONS_DIR / session_id

    if not session_dir.exists():
        return jsonify({'error': 'Session not found'}), 404

    transcription_file = session_dir / 'transcription.json'
    if not transcription_file.exists():
        return jsonify({'error': 'Transcription not found'}), 404

    try:
        with open(transcription_file, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    session_dir = SESSIONS_DIR / session_id

    if not session_dir.exists():
        return jsonify({'error': 'Session not found'}), 404

    try:
        shutil.rmtree(session_dir)
        return jsonify({'success': True, 'message': 'Session deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']

    session_id = str(uuid.uuid4())
    session_dir = SESSIONS_DIR / session_id
    session_dir.mkdir(exist_ok=True)

    audio_path = session_dir / 'original_audio.webm'
    audio_file.save(str(audio_path))
    temp_path = str(audio_path)

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

    return Response(stream_with_context(generate_segments()), mimetype='text/event-stream')

@app.route('/transcribe-live', methods=['POST'])
def transcribe_live():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio chunk provided'}), 400

    audio_chunk = request.files['audio']
    chunk_index = request.form.get('chunk_index', 0)
    session_id = request.form.get('session_id', 'default')

    print(f"\n[Server] Received chunk {chunk_index} for session {session_id}")

    session_dir = SESSIONS_DIR / session_id
    session_dir.mkdir(exist_ok=True)
    chunk_path = session_dir / f'chunk_{chunk_index}.webm'
    audio_chunk.save(str(chunk_path))
    chunk_size = os.path.getsize(str(chunk_path))
    temp_path = str(chunk_path)
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

    return Response(stream_with_context(generate_segments()), mimetype='text/event-stream')

if __name__ == '__main__':
    print("\n🎙️  Faster Whisper Real-time Transcription Server")
    print("=" * 50)
    print("Server starting on http://localhost:10000")
    print("Open your browser and start speaking!\n")
    app.run(debug=True, host='0.0.0.0', port=10000, use_reloader=False)
