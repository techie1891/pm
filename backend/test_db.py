import sqlite3
import tempfile
import os
from fastapi.testclient import TestClient

import main


def setup_client_with_tmpdb():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    # point the app to a temporary DB path
    main.DB_PATH = tmp.name
    main.init_db()
    client = TestClient(main.app)
    return client, tmp.name


def test_get_default_board():
    client, db = setup_client_with_tmpdb()
    res = client.get("/api/board/user")
    assert res.status_code == 200
    data = res.json()
    assert "columns" in data and isinstance(data["columns"], list)


def test_post_and_get_board():
    client, db = setup_client_with_tmpdb()
    payload = {
        "board": {
            "columns": [
                {"id": "todo", "title": "To Do", "cards": [{"id": "c1", "title": "Test Card", "details": "d"}]},
                {"id": "inprogress", "title": "In Progress", "cards": []},
                {"id": "done", "title": "Done", "cards": []},
            ]
        }
    }
    res = client.post("/api/board/user", json=payload)
    assert res.status_code == 200

    res2 = client.get("/api/board/user")
    assert res2.status_code == 200
    data = res2.json()
    assert any(col.get("id") == "todo" for col in data.get("columns", []))


def test_malformed_board_json_returns_500():
    client, db = setup_client_with_tmpdb()
    # insert malformed JSON directly into DB
    conn = sqlite3.connect(main.DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO boards (username, board_json, updated_at) VALUES (?, ?, ?)",
        ("user", "not-json", "now"),
    )
    conn.commit()
    conn.close()

    res = client.get("/api/board/user")
    assert res.status_code == 500
