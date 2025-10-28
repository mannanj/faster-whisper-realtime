#!/usr/bin/env python3
import os
import tempfile
from flask import Flask, request, jsonify, send_from_directory
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
    """Transcribe audio file sent from the client."""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']

    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
        audio_file.save(temp_audio.name)
        temp_path = temp_audio.name

    try:
        # Transcribe the audio
        segments, info = model.transcribe(temp_path, beam_size=5)

        # Collect all segments
        transcription = " ".join([segment.text for segment in segments])

        return jsonify({
            'transcription': transcription.strip(),
            'language': info.language,
            'duration': info.duration
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    print("\n🎙️  Faster Whisper Real-time Transcription Server")
    print("=" * 50)
    print("Server starting on http://localhost:10000")
    print("Open your browser and start speaking!\n")
    app.run(debug=True, host='0.0.0.0', port=10000, use_reloader=False)
