# 🎙️ Faster Whisper Real-time

**Speak. See text. That's it.**

A beautiful, minimal web interface for real-time speech transcription powered by [faster-whisper](https://github.com/SYSTRAN/faster-whisper).

## Why This Exists

Because speech-to-text shouldn't require a cloud API, a PhD, or patience. Just open your browser, click record, and watch your words appear.

## Features

- **Real-time transcription** - Speak naturally, get accurate text
- **Runs locally** - Your voice stays on your machine
- **Zero config** - Works out of the box
- **Beautiful UI** - Clean, gradient-powered interface
- **Language detection** - Automatically identifies what you're speaking

## Quick Start

```bash
git clone https://github.com/mannanj/faster-whisper-realtime.git
cd faster-whisper-realtime
./run.sh start
```

The script handles venv setup, dependencies, server launch, and opens your browser automatically.

## How It Works

1. Click "Start Recording"
2. Speak into your microphone
3. Click "Stop Recording"
4. Watch your speech become text

The first run downloads the model (~150MB for base model). Subsequent runs are instant.

## Requirements

- Python 3.8+
- A microphone
- Modern browser (Chrome, Firefox, Safari, Edge)

## Model Options

Default is `base` for speed/accuracy balance. Edit `server.py` line 13 to change:

- `tiny` - Fastest, least accurate
- `base` - **Default** - Great balance
- `small` - More accurate, slower
- `medium` - Very accurate, needs more RAM
- `large-v3` - Best accuracy, slowest

## Tech Stack

- **Backend**: Flask + faster-whisper
- **Frontend**: Vanilla JS + Modern CSS
- **ML**: OpenAI Whisper (via faster-whisper CTranslate2 implementation)

## License

MIT - Do whatever you want with it.

## Credits

Built with [faster-whisper](https://github.com/SYSTRAN/faster-whisper) by SYSTRAN.
