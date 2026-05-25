import sqlite3
import os
import json
import datetime
from main import DB_PATH, init_db


def seed_username(username: str = "user"):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM boards WHERE username = ?", (username,))
    if not c.fetchone():
        default = {
            "columns": [
                {"id": "todo", "title": "To Do", "cards": []},
                {"id": "inprogress", "title": "In Progress", "cards": []},
                {"id": "done", "title": "Done", "cards": []},
            ]
        }
        now = datetime.datetime.utcnow().isoformat() + "Z"
        c.execute(
            "INSERT OR REPLACE INTO boards (username, board_json, updated_at) VALUES (?, ?, ?)",
            (username, json.dumps(default), now),
        )
        conn.commit()
    conn.close()


if __name__ == "__main__":
    seed_username()
