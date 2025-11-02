# Task 21: Add JSON File Storage for Transcriptions

- [ ] Create storage directory structure for transcription data
- [ ] Implement backend endpoint to save transcriptions to JSON files
- [ ] Add metadata (timestamp, duration, language) to stored transcriptions
- [ ] Update frontend to trigger save on successful transcription
- [ ] Add option to view/list stored transcriptions
- **Location:** `server.py`, `index.html`

## Context/Design/Notes

Add local JSON file storage for transcriptions to persist user's transcription history. Each transcription should be saved with:
- Unique ID/timestamp
- Original audio metadata (duration, language)
- Transcription text
- Creation timestamp

Design considerations:
- Use simple JSON file per transcription for easy migration to database later
- Store in `data/transcriptions/` directory
- Filename format: `transcription_TIMESTAMP.json`
- Prepare structure for future universal database migration

Future migration path: JSON files → Universal database system
