#!/usr/bin/env python3
import os
import tempfile
import json
import time
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
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

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

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
