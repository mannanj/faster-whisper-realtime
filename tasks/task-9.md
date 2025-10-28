# Task 9: Background Compression Service (Optional)

- [ ] Create standalone compression service script `compression_service.py`
- [ ] Implement file age detection (scan recordings for files > 7 days old)
- [ ] Add FFmpeg integration for WebM → Opus conversion
- [ ] Implement compression with 96kbps bitrate
- [ ] Verify compressed file integrity before deleting originals
- [ ] Update metadata JSON files with compression info
- [ ] Update master index with new sizes
- [ ] Add logging for compression operations
- [ ] Create manual run command for testing
- [ ] Add cron job / scheduled task setup instructions
- [ ] Implement dry-run mode to preview actions
- [ ] Add configuration for compression policy (age threshold, bitrate, format)
- **Location:** New `compression_service.py`, update `server.py` for stats

## Purpose
Automatically compress old recordings to save disk space while maintaining audio quality. Runs as a background service or scheduled task to keep storage optimized.

## Compression Strategy

### Age-Based Policy
- **0-7 days:** Keep original WebM format (no compression)
- **7-30 days:** Convert to Opus 96kbps (~80% size reduction)
- **30+ days:** (Optional) Convert to Opus 64kbps or archive to cold storage

### Expected Savings
- WebM (original): ~1 MB/minute
- Opus 96kbps: ~0.7 MB/minute (720 KB/min)
- Opus 64kbps: ~0.5 MB/minute (480 KB/min)

Example: 100 hours of recordings
- Original: 6 GB
- Compressed (96kbps): 4.2 GB → **Save 1.8 GB**
- Compressed (64kbps): 3 GB → **Save 3 GB**

## Implementation

### compression_service.py

```python
#!/usr/bin/env python3
"""
Audio Compression Service

Scans recordings directory and compresses old files to save storage.
Run manually: python3 compression_service.py
Run with cron: 0 2 * * * cd /path/to/project && python3 compression_service.py
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
RECORDINGS_DIR = "recordings"
AGE_THRESHOLD_DAYS = 7
TARGET_BITRATE = "96k"  # Opus bitrate
DRY_RUN = False  # Set to True to preview without compressing

def find_old_recordings(age_days):
    """Find WebM files older than age_days."""
    cutoff_date = datetime.now() - timedelta(days=age_days)
    old_files = []

    for root, dirs, files in os.walk(RECORDINGS_DIR):
        for file in files:
            if file.endswith('.webm'):
                filepath = os.path.join(root, file)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))

                if file_time < cutoff_date:
                    old_files.append(filepath)

    return old_files

def compress_audio(input_path, output_path, bitrate="96k"):
    """Compress audio using FFmpeg with Opus codec."""
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-c:a', 'libopus',
        '-b:a', bitrate,
        '-vn',  # No video
        '-y',   # Overwrite output
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def verify_compression(original_path, compressed_path):
    """Verify compressed file is valid and smaller."""
    if not os.path.exists(compressed_path):
        return False

    original_size = os.path.getsize(original_path)
    compressed_size = os.path.getsize(compressed_path)

    # Should be smaller and non-zero
    if compressed_size >= original_size or compressed_size == 0:
        return False

    # Optional: Verify audio playback with ffprobe
    cmd = ['ffprobe', '-v', 'error', compressed_path]
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0

def update_metadata(webm_path, opus_path):
    """Update metadata JSON with compression info."""
    metadata_path = webm_path.replace('.webm', '.json')

    if not os.path.exists(metadata_path):
        return

    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    metadata['compressed'] = True
    metadata['original_size'] = os.path.getsize(webm_path)
    metadata['compressed_size'] = os.path.getsize(opus_path)
    metadata['compression_date'] = datetime.now().isoformat()
    metadata['compression_ratio'] = metadata['compressed_size'] / metadata['original_size']

    # Update chunk filenames from .webm to .opus
    for chunk in metadata.get('chunks', []):
        if chunk['file'].endswith('.webm'):
            chunk['file'] = chunk['file'].replace('.webm', '.opus')

    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

def compress_recordings(dry_run=False):
    """Main compression process."""
    old_files = find_old_recordings(AGE_THRESHOLD_DAYS)

    print(f"Found {len(old_files)} files older than {AGE_THRESHOLD_DAYS} days")

    if dry_run:
        print("\nDRY RUN - No files will be modified:")

    total_original_size = 0
    total_compressed_size = 0
    success_count = 0

    for webm_path in old_files:
        opus_path = webm_path.replace('.webm', '.opus')
        original_size = os.path.getsize(webm_path)

        print(f"\nProcessing: {webm_path}")
        print(f"  Original size: {original_size / 1024 / 1024:.2f} MB")

        if dry_run:
            estimated_compressed = original_size * 0.7  # Estimate 30% reduction
            print(f"  Estimated compressed: {estimated_compressed / 1024 / 1024:.2f} MB")
            continue

        # Compress
        if compress_audio(webm_path, opus_path, TARGET_BITRATE):
            compressed_size = os.path.getsize(opus_path)

            # Verify
            if verify_compression(webm_path, opus_path):
                # Update metadata
                update_metadata(webm_path, opus_path)

                # Delete original
                os.remove(webm_path)

                total_original_size += original_size
                total_compressed_size += compressed_size
                success_count += 1

                print(f"  ✓ Compressed to: {compressed_size / 1024 / 1024:.2f} MB")
                print(f"    Saved: {(original_size - compressed_size) / 1024 / 1024:.2f} MB")
            else:
                print(f"  ✗ Verification failed, keeping original")
                os.remove(opus_path)
        else:
            print(f"  ✗ Compression failed")

    # Summary
    print(f"\n{'=' * 50}")
    print(f"Compression Summary:")
    print(f"  Files processed: {success_count}/{len(old_files)}")
    if not dry_run:
        print(f"  Total original size: {total_original_size / 1024 / 1024:.2f} MB")
        print(f"  Total compressed size: {total_compressed_size / 1024 / 1024:.2f} MB")
        print(f"  Total saved: {(total_original_size - total_compressed_size) / 1024 / 1024:.2f} MB")
        print(f"  Compression ratio: {total_compressed_size / total_original_size * 100:.1f}%")

if __name__ == '__main__':
    import sys

    dry_run = '--dry-run' in sys.argv
    compress_recordings(dry_run=dry_run)
```

## Usage

### Manual Execution
```bash
# Preview what would be compressed
python3 compression_service.py --dry-run

# Actually compress files
python3 compression_service.py
```

### Scheduled Execution (Cron)

Add to crontab (`crontab -e`):
```bash
# Run compression service daily at 2 AM
0 2 * * * cd /Users/mannanj/Projects/faster-whisper-realtime && /usr/bin/python3 compression_service.py >> logs/compression.log 2>&1
```

Or use macOS launchd:
```xml
<!-- ~/Library/LaunchAgents/com.user.whisper-compression.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.whisper-compression</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/mannanj/Projects/faster-whisper-realtime/compression_service.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>2</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```

Load with: `launchctl load ~/Library/LaunchAgents/com.user.whisper-compression.plist`

## Configuration File (Optional)

Create `compression_config.json`:
```json
{
  "age_threshold_days": 7,
  "target_bitrate": "96k",
  "target_format": "opus",
  "delete_originals": true,
  "verify_before_delete": true,
  "log_file": "logs/compression.log",
  "dry_run": false
}
```

## Dependencies

System dependency:
```bash
# Install FFmpeg with Opus support
brew install ffmpeg  # macOS
apt install ffmpeg   # Linux
```

No additional Python packages needed (uses stdlib subprocess).

## Logging

Create `logs/` directory and write detailed logs:
```python
import logging

logging.basicConfig(
    filename='logs/compression.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info(f"Compressed {webm_path} → {opus_path}")
```

## Safety Features

1. **Verification:** Always verify compressed file before deleting original
2. **Dry run:** Test mode to preview actions
3. **Logging:** Detailed logs of all operations
4. **Metadata backup:** Keep original metadata even after compression
5. **Size check:** Verify compressed file is smaller than original
6. **Integrity check:** Use ffprobe to verify audio is playable

## Statistics Dashboard (Server Integration)

Add to `server.py`:
```python
@app.route('/api/storage-stats')
def storage_stats():
    total_size = 0
    compressed_size = 0

    for root, dirs, files in os.walk('recordings'):
        for file in files:
            if file.endswith(('.webm', '.opus')):
                filepath = os.path.join(root, file)
                size = os.path.getsize(filepath)
                total_size += size

                if file.endswith('.opus'):
                    compressed_size += size

    return jsonify({
        'total_size': total_size,
        'compressed_size': compressed_size,
        'original_size': total_size - compressed_size,
        'savings': total_size - compressed_size if compressed_size > 0 else 0,
        'compression_ratio': compressed_size / total_size if total_size > 0 else 0
    })
```

Display in recordings library UI.

## Testing

- Test with single old file (8 days old)
- Test with mix of old and new files
- Test dry-run mode
- Test verification failure handling
- Test metadata updates
- Verify playback of compressed files
- Test storage stats API
- Test cron/scheduled execution

## Future Enhancements

- Configurable compression policies per recording
- Multiple compression tiers (7 days, 30 days, 90 days)
- Archive to cloud storage (S3, Google Drive) for very old files
- Compression progress notifications
- Pause/resume compression for large batches
- Selective compression (compress only specific dates/languages)
