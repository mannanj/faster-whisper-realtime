# Task 3: Change default port from 5000 to avoid macOS conflicts

- [x] Choose alternative port (5001, 8000, or 8080)
- [x] Update server.py with new port
- [x] Update run.sh browser launch URL
- [x] Update run.sh stop command to use new port
- [x] Check index.html for hardcoded port references
- [x] Update README.md with new port
- [x] Update CLAUDE.md with new port references
- [x] Test server on new port
- **Location:** `server.py`, `run.sh`, `index.html`, `README.md`, `CLAUDE.md`

## Problem
Port 5000 is commonly used by macOS system services (AirPlay Receiver/ControlCenter and WebKit Networking), causing conflicts when trying to run the Flask server.

## Design Considerations
1. **Port choice**: Common alternatives:
   - 5001: Next sequential, familiar
   - 8000: Common Python development port
   - 8080: Traditional HTTP alternate
2. **Backward compatibility**: Document the change clearly
3. **Configuration**: Consider if port should be configurable (environment variable)
4. **All references**: Ensure all hardcoded port references are updated
5. **User experience**: Update stop command to match new port

**Recommended Port:** 8000 (common Python convention, less likely to conflict)
