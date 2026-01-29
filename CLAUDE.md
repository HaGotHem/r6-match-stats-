# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

R6 Siege Match Stats Analyzer - A Flask web application for analyzing Rainbow Six Siege match statistics from replay files (.rec format) and generating Excel reports.

**Version:** 3.0.0
**Platform:** Windows 10/11 (64-bit)
**Language:** Python 3.7+ with Flask backend, vanilla JavaScript frontend

## Commands

```bash
# Run from source
python main.py
# or
python web/app.py

# Install dependencies
pip install -r requirements.txt

# Build executable with PyInstaller
python -m PyInstaller R6Analyst.spec
```

## Architecture

```
r6_analyst/
├── main.py                    # PyInstaller entry point, launches Flask + browser
├── START_WEB_APP.bat          # Windows launcher (detects Python, installs deps)
├── web/
│   ├── app.py                 # Flask server - all API routes (~650 lines)
│   └── templates/
│       └── index.html         # Single-page UI with tabs (~1200 lines)
├── src/
│   └── analyze_match_complete.py  # Core stats engine - pandas/openpyxl (~490 lines)
├── tools/
│   └── r6-dissect.exe         # Binary parser for .rec files (external tool v0.24.0)
└── data/                      # Runtime data (not versioned)
    ├── uploads/               # Uploaded .rec files
    ├── match_data/            # Temporary JSON from r6-dissect
    ├── reports/               # Generated Excel reports
    └── config.json            # User configuration (game_path, replay_path)
```

## Data Flow

1. **User selects matches** in web UI
2. **Flask** calls `r6-dissect.exe` to parse .rec files → JSON
3. **analyze_match_complete.py** aggregates JSON data → pandas DataFrame
4. **openpyxl** formats and styles → Excel workbook
5. **User downloads** the report

## Key API Endpoints

| Route | Purpose |
|-------|---------|
| `GET /api/config` | Load user configuration |
| `POST /api/config` | Save game path |
| `GET /api/detect-game` | Auto-detect R6 installation |
| `GET /api/replays` | Scan MatchReplay folder |
| `POST /api/analyze` | Analyze selected matches |
| `POST /upload` | Upload .rec files (legacy) |
| `GET /download/<filename>` | Download Excel report |

## Statistics Categories

9 stat categories configurable in UI: Kills/Deaths, KOST%, Survival, Headshots, Opening Kills/Deaths, Multi-kills, Plants/Defuses, Teamkills, Rating. Each calculated for ATK/DEF/GLOBAL sides.

## Code Conventions

- French comments and variable names throughout
- Debug output prefixed with `[DEBUG]`, `[ERROR]`, `[OK]`
- Configuration persisted in `data/config.json`
- r6-dissect.exe is an external binary dependency - do not modify

## Known Limitations

- r6-dissect v0.24.0 may not recognize operators from Y10S4_01+
- Windows-only (hardcoded paths)
- Port 5000 must be available
