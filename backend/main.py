from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import sqlite3
import json
import datetime
import uuid
from pydantic import BaseModel

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


def migrate_board_shape():
    """Scan existing boards and migrate any old array-of-cards shape to map-shape.

    Old shape example: columns: [{id,title,cards: [{id,title,details},...]},...]
    New (preferred) shape: columns: [{id,title,cardIds: [...]},...], cards: { id: {..} }
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, board_json FROM boards")
    rows = c.fetchall()
    updated = 0
    for username, board_json in rows:
        try:
            board = json.loads(board_json)
        except Exception:
            continue

        needs_migration = False
        cards_map = {}
        for col in board.get("columns", []):
            if isinstance(col.get("cards"), list) and not isinstance(col.get("cardIds"), list):
                needs_migration = True
        if not needs_migration:
            continue

        # perform migration
        for col in board.get("columns", []):
            col_cards = col.pop("cards", [])
            card_ids = []
            for cobj in col_cards:
                cid = cobj.get("id") or str(uuid.uuid4())
                card_ids.append(cid)
                cards_map[cid] = {
                    "id": cid,
                    "title": cobj.get("title", "Untitled"),
                    "details": cobj.get("details", cobj.get("description", "")),
                }
            col["cardIds"] = card_ids

        board["cards"] = {**board.get("cards", {}), **cards_map}

        c.execute(
            "INSERT OR REPLACE INTO boards (username, board_json, updated_at) VALUES (?, ?, datetime('now'))",
            (username, json.dumps(board)),
        )
        updated += 1

    conn.commit()
    conn.close()
    return updated


@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize DB and run migrations
    init_db()
    migrate_board_shape()
    yield


app = FastAPI(lifespan=lifespan)


# API routes


@app.get("/api/hello")
def api_hello():
    return {"message": "hello"}


class BoardIn(BaseModel):
    board: dict


@app.get("/api/board/{username}")
def get_board(username: str):
    board = _load_board_raw(username)
    return board


def _load_board_raw(username: str):
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


def _save_board_raw(username: str, board_obj: dict):
    board_json = json.dumps(board_obj)
    now = datetime.datetime.utcnow().isoformat() + "Z"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO boards (username, board_json, updated_at) VALUES (?, ?, ?)",
        (username, board_json, now),
    )
    conn.commit()
    conn.close()
    return now


@app.post("/api/board/{username}")
def save_board(username: str, payload: BoardIn):
    now = _save_board_raw(username, payload.board)
    return {"status": "ok", "updated_at": now}


# Additional CRUD endpoints for cards and columns


class CardIn(BaseModel):
    id: str | None = None
    title: str
    details: str | None = ""


class CardCreate(BaseModel):
    column_id: str
    card: CardIn


@app.post("/api/board/{username}/cards")
def create_card(username: str, payload: CardCreate):
    board = _load_board_raw(username)
    # Determine board shape
    is_map_shape = isinstance(board.get("cards"), dict)

    card_id = payload.card.id or str(uuid.uuid4())
    new_card = {"id": card_id, "title": payload.card.title, "details": payload.card.details}

    if is_map_shape:
        # ensure cards map
        cards = board.setdefault("cards", {})
        cards[card_id] = new_card
        # append to column.cardIds
        for col in board.get("columns", []):
            if col.get("id") == payload.column_id:
                col_card_ids = col.setdefault("cardIds", [])
                col_card_ids.append(card_id)
                break
    else:
        # array-of-cards shape
        for col in board.get("columns", []):
            if col.get("id") == payload.column_id:
                col_cards = col.setdefault("cards", [])
                col_cards.append(new_card)
                break

    now = _save_board_raw(username, board)
    return {"status": "ok", "updated_at": now, "card": new_card}


class CardUpdate(BaseModel):
    title: str | None = None
    details: str | None = None


@app.put("/api/board/{username}/cards/{card_id}")
def update_card(username: str, card_id: str, payload: CardUpdate):
    board = _load_board_raw(username)
    is_map_shape = isinstance(board.get("cards"), dict)
    updated = None

    if is_map_shape:
        cards = board.get("cards", {})
        if card_id in cards:
            if payload.title is not None:
                cards[card_id]["title"] = payload.title
            if payload.details is not None:
                cards[card_id]["details"] = payload.details
            updated = cards[card_id]
    else:
        for col in board.get("columns", []):
            for c in col.get("cards", []):
                if c.get("id") == card_id:
                    if payload.title is not None:
                        c["title"] = payload.title
                    if payload.details is not None:
                        c["details"] = payload.details
                    updated = c
                    break
            if updated:
                break

    if not updated:
        raise HTTPException(status_code=404, detail="card not found")

    now = _save_board_raw(username, board)
    return {"status": "ok", "updated_at": now, "card": updated}


@app.delete("/api/board/{username}/cards/{card_id}")
def delete_card(username: str, card_id: str):
    board = _load_board_raw(username)
    is_map_shape = isinstance(board.get("cards"), dict)
    removed = False

    if is_map_shape:
        cards = board.get("cards", {})
        if card_id in cards:
            del cards[card_id]
            removed = True
        # remove from any column.cardIds
        for col in board.get("columns", []):
            col_card_ids = col.get("cardIds", [])
            if card_id in col_card_ids:
                col["cardIds"] = [cid for cid in col_card_ids if cid != card_id]
    else:
        for col in board.get("columns", []):
            col_cards = col.get("cards", [])
            new_cards = [c for c in col_cards if c.get("id") != card_id]
            if len(new_cards) != len(col_cards):
                col["cards"] = new_cards
                removed = True

    if not removed:
        raise HTTPException(status_code=404, detail="card not found")

    now = _save_board_raw(username, board)
    return {"status": "ok", "updated_at": now}


class ActionsIn(BaseModel):
    actions: list


@app.post("/api/board/{username}/apply-actions")
def apply_actions(username: str, payload: ActionsIn):
    board = _load_board_raw(username)
    actions = payload.actions or []
    # apply sequentially
    for act in actions:
        t = act.get("type")
        p = act.get("payload") or {}
        if t == "add_card":
            col_id = p.get("column_id")
            card = p.get("card")
            if not col_id or not card:
                continue
            # reuse create logic
            cid = card.get("id") or str(uuid.uuid4())
            new_card = {"id": cid, "title": card.get("title", "Untitled"), "details": card.get("details", "")}
            if isinstance(board.get("cards"), dict):
                board.setdefault("cards", {})[cid] = new_card
                for col in board.get("columns", []):
                    if col.get("id") == col_id:
                        col.setdefault("cardIds", []).append(cid)
                        break
            else:
                for col in board.get("columns", []):
                    if col.get("id") == col_id:
                        col.setdefault("cards", []).append(new_card)
                        break
        elif t == "update_column":
            col_id = p.get("column_id")
            title = p.get("title")
            for col in board.get("columns", []):
                if col.get("id") == col_id:
                    col["title"] = title
                    break
        elif t == "delete_card":
            card_id = p.get("card_id")
            if not card_id:
                continue
            if isinstance(board.get("cards"), dict):
                if card_id in board.get("cards", {}):
                    del board["cards"][card_id]
                for col in board.get("columns", []):
                    col["cardIds"] = [cid for cid in col.get("cardIds", []) if cid != card_id]
            else:
                for col in board.get("columns", []):
                    col["cards"] = [c for c in col.get("cards", []) if c.get("id") != card_id]
        elif t == "move_card":
            # payload: {card_id, to_column_id, to_index (optional)}
            card_id = p.get("card_id")
            to_col = p.get("to_column_id")
            to_index = p.get("to_index")
            if not card_id or not to_col:
                continue
            # remove from existing
            removed_card = None
            if isinstance(board.get("cards"), dict):
                for col in board.get("columns", []):
                    if card_id in col.get("cardIds", []):
                        col["cardIds"] = [cid for cid in col.get("cardIds", []) if cid != card_id]
                        removed_card = board.get("cards", {}).get(card_id)
                        break
                # insert into target
                for col in board.get("columns", []):
                    if col.get("id") == to_col:
                        ids = col.setdefault("cardIds", [])
                        if to_index is None:
                            ids.append(card_id)
                        else:
                            idx = max(0, min(len(ids), int(to_index)))
                            ids.insert(idx, card_id)
                        break
            else:
                # array-of-cards
                for col in board.get("columns", []):
                    new_cards = [c for c in col.get("cards", []) if c.get("id") != card_id]
                    if len(new_cards) != len(col.get("cards", [])):
                        col["cards"] = new_cards
                for col in board.get("columns", []):
                    if col.get("id") == to_col:
                        if to_index is None:
                            col.setdefault("cards", []).append({"id": card_id})
                        else:
                            idx = max(0, min(len(col.get("cards", [])), int(to_index)))
                            col.setdefault("cards", []).insert(idx, {"id": card_id})
                        break
        else:
            # unknown action: ignore
            continue

    now = _save_board_raw(username, board)
    return {"status": "ok", "updated_at": now, "board": board}


class ColumnIn(BaseModel):
    id: str | None = None
    title: str


@app.post("/api/board/{username}/columns")
def create_column(username: str, payload: ColumnIn):
    board = _load_board_raw(username)
    col_id = payload.id or str(uuid.uuid4())
    # prefer map-shape format cardIds, but accept existing format
    sample_col = board.get("columns", [{}])[0] if board.get("columns") else {}
    uses_cardIds = isinstance(sample_col.get("cardIds"), list)

    new_col = {"id": col_id, "title": payload.title}
    if uses_cardIds:
        new_col["cardIds"] = []
    else:
        new_col["cards"] = []

    board.setdefault("columns", []).append(new_col)
    now = _save_board_raw(username, board)
    return {"status": "ok", "updated_at": now, "column": new_col}


@app.put("/api/board/{username}/columns/{column_id}")
def update_column(username: str, column_id: str, payload: ColumnIn):
    board = _load_board_raw(username)
    updated = None
    for col in board.get("columns", []):
        if col.get("id") == column_id:
            col["title"] = payload.title
            updated = col
            break
    if not updated:
        raise HTTPException(status_code=404, detail="column not found")
    now = _save_board_raw(username, board)
    return {"status": "ok", "updated_at": now, "column": updated}


@app.delete("/api/board/{username}/columns/{column_id}")
def delete_column(username: str, column_id: str):
    board = _load_board_raw(username)
    cols = board.get("columns", [])
    new_cols = [c for c in cols if c.get("id") != column_id]
    if len(new_cols) == len(cols):
        raise HTTPException(status_code=404, detail="column not found")

    # If using map-shape, remove cards from cards map, else drop card objects
    sample_col = cols[0] if cols else {}
    is_map_shape = isinstance(board.get("cards"), dict)
    if is_map_shape:
        # collect removed card ids
        removed_ids = []
        for c in cols:
            if c.get("id") == column_id:
                removed_ids = c.get("cardIds", [])
                break
        cards_map = board.get("cards", {})
        for rid in removed_ids:
            if rid in cards_map:
                del cards_map[rid]
    else:
        # nothing special — dropping the column removes the nested card objects
        pass

    board["columns"] = new_cols
    now = _save_board_raw(username, board)
    return {"status": "ok", "updated_at": now}


# Note: static mount moved to end of file so it does not intercept API routes


# AI helper endpoints
try:
    import httpx
except Exception:
    httpx = None

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://api.openrouter.ai/v1/chat/completions"


class AIRequest(BaseModel):
    prompt: str


@app.post("/api/ai/compute")
def ai_compute(req: AIRequest):
    # Proxy to OpenRouter when API key is present
    if OPENROUTER_KEY and httpx:
        try:
            payload = {
                "model": "openai/gpt-oss-120b",
                "messages": [{"role": "user", "content": req.prompt}],
                "max_tokens": 200,
            }
            headers = {"Authorization": f"Bearer {OPENROUTER_KEY}"}
            r = httpx.post(OPENROUTER_URL, json=payload, timeout=30.0, headers=headers)
            r.raise_for_status()
            data = r.json()
            choices = data.get("choices") or []
            text = ""
            if choices:
                text = choices[0].get("message", {}).get("content", "")
            return {"result": text, "raw": data}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Fallback: simple arithmetic evaluator for basic expressions like "2+2"
    expr = req.prompt.strip()
    try:
        import re

        if re.fullmatch(r"[0-9+\-*/ ().]+", expr):
            result = eval(expr, {"__builtins__": {}}, {})
            return {"result": str(result), "raw": None}
    except Exception:
        pass
    return {"result": f"Mock response for: {req.prompt}"}


class AIModifyRequest(BaseModel):
    prompt: str
    board: dict


@app.post("/api/ai/modify-board")
def ai_modify_board(req: AIModifyRequest):
    # If OpenRouter is configured, ask it to suggest JSON actions.
    if OPENROUTER_KEY and httpx:
        try:
            system = {
                "role": "system",
                "content": (
                    "You are an assistant that returns JSON instructions to modify a Kanban board. "
                    "Respond ONLY with JSON: { actions: [ {type: 'add_card'|'move_card'|'update_column'|'delete_card', payload: {...} } ] }"
                ),
            }
            user = {"role": "user", "content": f"Board: {json.dumps(req.board)}\nPrompt: {req.prompt}"}
            payload = {"model": "openai/gpt-oss-120b", "messages": [system, user], "max_tokens": 512}
            headers = {"Authorization": f"Bearer {OPENROUTER_KEY}"}
            r = httpx.post(OPENROUTER_URL, json=payload, timeout=30.0, headers=headers)
            r.raise_for_status()
            data = r.json()
            choices = data.get("choices") or []
            text = ""
            if choices:
                text = choices[0].get("message", {}).get("content", "")
            try:
                parsed = json.loads(text)
                return {"ok": True, "suggested": parsed}
            except Exception:
                return {"ok": False, "error": "AI returned non-JSON", "raw": text}
        except Exception as e:
            # If the external AI call fails (network/DNS/etc), fall back to mock behavior
            print("OpenRouter call failed, falling back to mock:", e)
            # continue to fallback mock below
            pass

    # Fallback: simple mock — add a card to first column
    board = req.board
    cols = board.get("columns", [])
    if not cols:
        return {"ok": False, "error": "No columns"}
    first_col = cols[0]
    cid = str(uuid.uuid4())
    card = {"id": cid, "title": f"AI: {req.prompt}", "details": "Added by AI (mock)"}
    if isinstance(board.get("cards"), dict):
        board.setdefault("cards", {})[cid] = card
        first_col.setdefault("cardIds", []).append(cid)
    else:
        first_col.setdefault("cards", []).append(card)

    return {"ok": True, "suggested": {"actions": [{"type": "add_card", "payload": {"column_id": first_col.get("id"), "card": card}}]}, "board": board}


# Serve static files from frontend build (if present)
public_dir = os.path.join(os.path.dirname(__file__), "public")
if os.path.exists(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="frontend")

