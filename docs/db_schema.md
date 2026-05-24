# Database schema for PM MVP

This document describes the SQLite schema used to persist Kanban boards for the MVP.

Design goals
- Minimal complexity: use SQLite bundled with Python; avoid ORMs for MVP.
- Single table to store per‑user board JSON blobs.
- Schema is easy to extend with metadata columns later.

Schema
- Table: `boards`
  - `username` TEXT PRIMARY KEY — unique identifier for the user (MVP uses a single hardcoded user).
  - `board_json` TEXT NOT NULL — JSON string containing the serialized Kanban board (columns, cards, positions, IDs).
  - `updated_at` TEXT NOT NULL — ISO 8601 timestamp of the last update (UTC).

Example row
```
username: "user"
board_json: '{"columns":[{"id":"todo","title":"To Do","cards":[]},{"id":"inprogress","title":"In Progress","cards":[]},{"id":"done","title":"Done","cards":[]}]}'
updated_at: "2026-05-24T07:00:00.000Z"
```

Access patterns
- Read: fetch a user's board by `username` to render the UI.
- Write: replace the JSON blob for the user when the frontend saves changes.

Rationale
- Storing the board as JSON keeps the backend schema simple and flexible for the MVP.
- If finer queries are required later (search cards, card history), we can normalize into additional tables.

Migration & initialization
- The backend will create the `boards` table automatically at startup if it does not exist.
