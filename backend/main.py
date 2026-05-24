from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import sqlite3
import json
import datetime

app = FastAPI()

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "kanban.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS boards (
            username TEXT PRIMARY KEY,
            board_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


@app.on_event("startup")
def startup_event():
    init_db()


# API routes


@app.get("/api/hello")
def api_hello():
    return {"message": "hello"}


class BoardIn(BaseModel):
    board: dict


@app.get("/api/board/{username}")
def get_board(username: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT board_json FROM boards WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        try:
            return json.loads(row[0])
        except Exception:
            raise HTTPException(status_code=500, detail="Malformed board JSON")

    # Default empty board template
    default = {
        "columns": [
            {"id": "todo", "title": "To Do", "cards": []},
            {"id": "inprogress", "title": "In Progress", "cards": []},
            {"id": "done", "title": "Done", "cards": []},
        ]
    }
    return default


@app.post("/api/board/{username}")
def save_board(username: str, payload: BoardIn):
    board_json = json.dumps(payload.board)
    now = datetime.datetime.utcnow().isoformat() + "Z"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO boards (username, board_json, updated_at) VALUES (?, ?, ?)",
        (username, board_json, now),
    )
    conn.commit()
    conn.close()
    return {"status": "ok", "updated_at": now}


# Serve static files from frontend build (if present)
public_dir = os.path.join(os.path.dirname(__file__), "public")
if os.path.exists(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="frontend")

