# Task 6: Audio Archive System with Compression

- [ ] Create `recordings/` directory structure with date-based organization
- [ ] Implement audio chunking for recordings > 2-3 minutes
- [ ] Save recordings with timestamp-based filenames
- [ ] Generate metadata JSON sidecar files for each recording
- [ ] Create master index.json for fast listing
- [ ] Implement background compression service (WebM → Opus)
- [ ] Add compression age policy (convert files older than 7 days)
- [ ] Add storage statistics tracking
- [ ] Update `/transcribe` endpoint to save audio and metadata
- **Location:** `server.py`, new `recordings/` directory, new `compression_service.py`

## Purpose
Automatically save all transcribed audio files with intelligent compression to minimize storage while preserving recordings for playback, review, and future reference.

## File Structure
```
recordings/
├── 2025-10-27/
│   ├── 14-30-45-chunk-1.webm
│   ├── 14-30-45-chunk-1.json
│   ├── 14-30-45-chunk-2.webm
│   ├── 14-30-45-chunk-2.json
│   └── ...
├── 2025-10-28/
│   └── ...
└── index.json  # Master index for fast queries
```

## Metadata JSON Format
```json
{
  "id": "2025-10-27T14:30:45Z",
  "timestamp": "2025-10-27T14:30:45Z",
  "date": "2025-10-27",
  "time": "14:30:45",
  "duration": 145.2,
  "language": "en",
  "chunks": [
    {
      "file": "14-30-45-chunk-1.webm",
      "start": 0,
      "end": 120,
      "duration": 120,
      "segments": [
        {"start": 0.0, "end": 2.5, "text": "Hello world"},
        {"start": 2.5, "end": 5.0, "text": "this is a test"}
      ]
    },
    {
      "file": "14-30-45-chunk-2.webm",
      "start": 120,
      "end": 145.2,
      "duration": 25.2,
      "segments": [
        {"start": 120.0, "end": 122.8, "text": "another segment"}
      ]
    }
  ],
  "full_transcription": "Hello world this is a test another segment",
  "compressed": false,
  "original_size": 1024000,
  "compressed_size": null,
  "compression_date": null
}
```

## Implementation Steps

### 1. Audio Chunking
Use `pydub` or `ffmpeg` to split long recordings into 2-3 minute chunks:
```python
from pydub import AudioSegment

def chunk_audio(audio_path, chunk_length_ms=120000):  # 2 minutes
    audio = AudioSegment.from_file(audio_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]
        chunks.append(chunk)
    return chunks
```

### 2. Save with Metadata
```python
def save_recording(audio_file, segments, info):
    timestamp = datetime.now()
    date_dir = timestamp.strftime("%Y-%m-%d")
    time_str = timestamp.strftime("%H-%M-%S")

    # Create directory structure
    recording_dir = f"recordings/{date_dir}"
    os.makedirs(recording_dir, exist_ok=True)

    # Save audio chunks and build metadata
    metadata = {
        "id": timestamp.isoformat(),
        "timestamp": timestamp.isoformat(),
        "date": date_dir,
        "time": time_str,
        "duration": info.duration,
        "language": info.language,
        "chunks": [],
        "full_transcription": "",
        "compressed": False,
        "original_size": os.path.getsize(audio_file)
    }

    # Save chunks and collect segments
    # Update index.json
```

### 3. Background Compression Service
Create `compression_service.py`:
```python
# Scan recordings/ for files older than 7 days
# Convert WebM → Opus using ffmpeg:
#   ffmpeg -i input.webm -c:a libopus -b:a 96k output.opus
# Update metadata JSON with compression info
# Delete original WebM after successful compression
```

### 4. Compression Command
```bash
ffmpeg -i recording.webm -c:a libopus -b:a 96k -vn recording.opus
```

## Compression Policy
- **0-7 days:** Keep original WebM format
- **7+ days:** Convert to Opus (96kbps) - ~80% size reduction
- **Optional:** Delete originals after 30 days if Opus verified

## Dependencies
```
pydub==0.25.1          # Audio manipulation
ffmpeg-python==0.2.0    # Python FFmpeg wrapper
```

Plus system dependency: `ffmpeg` (with libopus support)

## Master Index Format
```json
{
  "recordings": [
    {
      "id": "2025-10-27T14:30:45Z",
      "date": "2025-10-27",
      "time": "14:30:45",
      "duration": 145.2,
      "language": "en",
      "transcription_preview": "Hello world this is a test...",
      "chunks": 2,
      "compressed": false,
      "size": 1024000
    }
  ],
  "total_recordings": 1,
  "total_duration": 145.2,
  "total_size": 1024000,
  "compressed_size": 0,
  "last_updated": "2025-10-27T14:30:45Z"
}
```

## Testing
- Test single short recording (< 30s)
- Test long recording requiring chunking (5+ minutes)
- Verify metadata JSON accuracy
- Test manual compression on old file
- Verify index.json updates correctly
