from fastapi.testclient import TestClient
import json
import tempfile

import main


def setup_client_tmpdb():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    main.DB_PATH = tmp.name
    main.init_db()
    return TestClient(main.app)


def test_create_update_delete_card():
    client = setup_client_tmpdb()
    # create a column first
    res_col = client.post("/api/board/user/columns", json={"title": "Col A"})
    assert res_col.status_code == 200
    col = res_col.json()["column"]
    col_id = col["id"]

    # create a card in the column
    payload = {"column_id": col_id, "card": {"title": "Card 1", "details": "d"}}
    res = client.post("/api/board/user/cards", json=payload)
    assert res.status_code == 200
    card = res.json()["card"]
    card_id = card["id"]

    # update card
    res_up = client.put(f"/api/board/user/cards/{card_id}", json={"title": "Card 1a"})
    assert res_up.status_code == 200
    assert res_up.json()["card"]["title"] == "Card 1a"

    # delete card
    res_del = client.delete(f"/api/board/user/cards/{card_id}")
    assert res_del.status_code == 200


def test_create_update_delete_column():
    client = setup_client_tmpdb()
    # create column
    res = client.post("/api/board/user/columns", json={"title": "Col X"})
    assert res.status_code == 200
    col = res.json()["column"]
    cid = col["id"]

    # update
    res_up = client.put(f"/api/board/user/columns/{cid}", json={"title": "Col X2"})
    assert res_up.status_code == 200
    assert res_up.json()["column"]["title"] == "Col X2"

    # delete
    res_del = client.delete(f"/api/board/user/columns/{cid}")
    assert res_del.status_code == 200


def test_apply_actions_add_card():
    client = setup_client_tmpdb()
    # create a column
    res = client.post("/api/board/user/columns", json={"title": "AI Col"})
    assert res.status_code == 200
    col = res.json()["column"]
    cid = col["id"]

    actions = [{"type": "add_card", "payload": {"column_id": cid, "card": {"title": "AI Card", "details": "from ai"}}}]
    res2 = client.post("/api/board/user/apply-actions", json={"actions": actions})
    assert res2.status_code == 200
    body = res2.json()
    assert body.get("board")
    # new card should be in the board
    board = body.get("board")
    if isinstance(board.get("cards"), dict):
        assert any(c.get("title") == "AI Card" for c in board.get("cards", {}).values())
    else:
        assert any(any(c.get("title") == "AI Card" for c in col.get("cards", [])) for col in board.get("columns", []))
