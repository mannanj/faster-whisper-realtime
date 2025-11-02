# Task 38: Permanent Storage for Transcripts and Audio

- [x] Remove SESSION_TIMEOUT constant
- [x] Remove cleanup_old_sessions function
- [x] Remove cleanup_old_sessions call from /transcribe-file endpoint
- [x] Remove all temporary file usage in favor of permanent storage
- [x] Update audio saving to use data/sessions directory
- [x] Verify no other cleanup/deletion logic exists
- **Location:** `server.py`

## Context

Currently, the server deletes old transcription sessions after a timeout period (SESSION_TIMEOUT). The `cleanup_old_sessions()` function (lines 70-77) removes session directories that exceed the age threshold, causing permanent data loss.

Additionally, audio files are saved to temporary files (`tempfile.NamedTemporaryFile`) which may be automatically deleted by the OS.

## Design

### Remove Automatic Cleanup

1. **Delete SESSION_TIMEOUT constant**
   - Likely defined near top of server.py
   - Remove the variable entirely

2. **Delete cleanup_old_sessions function**
   - Remove lines 70-77
   - Function deletes directories from data/sessions

3. **Remove cleanup call**
   - Line 112: `cleanup_old_sessions()` called in `/transcribe-file` route
   - Remove this function call

### Permanent Audio Storage

Current temporary file usage:
```python
# Line 123
with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_audio:
    audio_file.save(temp_audio.name)
    temp_path = temp_audio.name

# Line 361
with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
    audio_file.save(temp_audio.name)
    temp_path = temp_audio.name

# Line 401
with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
    audio_chunk.save(temp_audio.name)
    temp_path = temp_audio.name
```

**Issues with current approach:**
- Files saved to `/tmp` directory (OS-managed, may be cleared on reboot)
- `delete=False` prevents immediate deletion, but files accumulate in /tmp
- No explicit cleanup of these temp files after processing
- Not properly moved to permanent storage

**Solution:**
Save directly to `data/sessions/<session_id>/` directory:

```python
# Instead of tempfile, use session directory
session_dir = SESSIONS_DIR / session_id
session_dir.mkdir(exist_ok=True)

# For main audio file
audio_path = session_dir / 'original_audio.webm'
audio_file.save(str(audio_path))

# For chunks in real-time
chunk_path = session_dir / f'chunk_{chunk_index}.webm'
audio_chunk.save(str(chunk_path))
```

### File Locations to Update

1. **Line 123** (`/transcribe-file` route):
   ```python
   # Change from:
   with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_audio:
       audio_file.save(temp_audio.name)
       temp_path = temp_audio.name

   # To:
   audio_path = session_dir / 'original_audio.webm'
   audio_file.save(str(audio_path))
   temp_path = str(audio_path)
   ```

2. **Line 361** (`/transcribe` route - single file):
   - Similar change as above
   - Save to session directory if session tracking exists
   - Or create unique filename in data/sessions

3. **Line 401** (`/transcribe-live` route - streaming chunks):
   ```python
   # Change from:
   with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
       audio_chunk.save(temp_audio.name)
       temp_path = temp_audio.name

   # To:
   session_dir = SESSIONS_DIR / session_id
   session_dir.mkdir(exist_ok=True)
   chunk_path = session_dir / f'chunk_{chunk_index}.webm'
   audio_chunk.save(str(chunk_path))
   temp_path = str(chunk_path)
   ```

### Preserve User-Initiated Deletion

Keep the `/session/<session_id>` DELETE endpoint (lines 342-352). This allows users to manually delete sessions through the UI, which is intentional and user-controlled.

## Implementation Steps

1. **Find and remove SESSION_TIMEOUT**
   - Search for constant definition
   - Likely at top with other config

2. **Remove cleanup_old_sessions function**
   - Lines 70-77
   - Entire function can be deleted

3. **Remove cleanup call**
   - Line 112 in `/transcribe-file` route
   - Delete the function invocation

4. **Update file saving in /transcribe-file** (line 123):
   - Replace tempfile with session_dir path
   - Save as `original_audio.webm` or similar

5. **Update file saving in /transcribe** (line 361):
   - Same change as above
   - Ensure session tracking or unique naming

6. **Update file saving in /transcribe-live** (line 401):
   - Save chunks to session directory
   - Use format like `chunk_0.webm`, `chunk_1.webm`, etc.

7. **Verify all temp files cleaned up**
   - Search codebase for `tempfile`
   - Ensure no other usages remain
   - Check for manual `/tmp/` paths

## Testing Checklist

- [ ] SESSION_TIMEOUT constant removed
- [ ] cleanup_old_sessions function removed
- [ ] cleanup_old_sessions() call removed from /transcribe-file
- [ ] Audio files saved to data/sessions/<session_id>/ directory
- [ ] No files saved to /tmp directory
- [ ] Upload new file → verify audio saved in data/sessions
- [ ] Real-time transcription → verify chunks saved in data/sessions
- [ ] Old sessions persist after server restart
- [ ] User-initiated deletion still works (History tab → Delete button)
- [ ] No tempfile imports or usage remain (except for legitimate temporary processing)

## Verification Commands

```bash
# After running server and creating sessions:

# Check that sessions persist
ls -la data/sessions/

# Verify audio files are in session dirs
find data/sessions -name "*.webm" -o -name "*.mp3"

# Ensure no temp files in /tmp
ls /tmp | grep -i "whisper\|transcribe\|audio"

# Check code for remaining tempfile usage
grep -n "tempfile" server.py
grep -n "/tmp" server.py
```

## Notes

- Keep existing session structure intact (transcription.json, status.json, etc.)
- This change makes all transcripts permanent until manually deleted
- Disk usage will grow over time → may want to add user-facing storage management later
- Consider adding total storage display in History tab (future enhancement)
