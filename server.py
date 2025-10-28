#!/usr/bin/env python3
import os
import tempfile
import json
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
from faster_whisper import WhisperModel

app = Flask(__name__, static_folder='.')
CORS(app)

# Initialize the model (using base model for balance of speed and accuracy)
# Options: tiny, base, small, medium, large-v2, large-v3
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
            segments, info = model.transcribe(temp_path, beam_size=5)

            yield f"data: {json.dumps({'type': 'metadata', 'language': info.language, 'duration': info.duration})}\n\n"

            for segment in segments:
                yield f"data: {json.dumps({'type': 'segment', 'start': segment.start, 'end': segment.end, 'text': segment.text})}\n\n"

            yield f"data: {json.dumps({'type': 'complete'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    return Response(stream_with_context(generate_segments()), mimetype='text/event-stream')

if __name__ == '__main__':
    print("\n🎙️  Faster Whisper Real-time Transcription Server")
    print("=" * 50)
    print("Server starting on http://localhost:10000")
    print("Open your browser and start speaking!\n")
    app.run(debug=True, host='0.0.0.0', port=10000, use_reloader=False)
