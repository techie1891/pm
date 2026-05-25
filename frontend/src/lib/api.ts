import type { BoardData, Card, Column } from "./kanban";

const normalizeServerBoard = (raw: any): BoardData => {
  if (!raw || !Array.isArray(raw.columns)) {
    return { columns: [], cards: {} };
  }

  // If server returns columns with `cardIds`, assume it's already our shape
  const first = raw.columns[0];
  if (first && Array.isArray(first.cardIds)) {
    // ensure cards object exists
    return {
      columns: raw.columns as Column[],
      cards: raw.cards || {},
    } as BoardData;
  }

  // If server returns columns with `cards` arrays (list of card objects), convert
  const cards: Record<string, Card> = {};
  const columns: Column[] = raw.columns.map((col: any) => {
    const colCards = Array.isArray(col.cards) ? col.cards : [];
    const cardIds: string[] = colCards.map((c: any) => {
      const id = c.id || `card-${Math.random().toString(36).slice(2, 8)}`;
      cards[id] = {
        id,
        title: c.title || "Untitled",
        details: c.details || c.description || "",
      };
      return id;
    });
    return { id: col.id || `col-${Math.random().toString(36).slice(2, 6)}`, title: col.title || "", cardIds };
  });

  return { columns, cards } as BoardData;
};

const API = {
  fetchBoard: async (username = "user"): Promise<BoardData> => {
    const res = await fetch(`/api/board/${encodeURIComponent(username)}`);
    if (!res.ok) throw new Error("Failed to fetch board");
    const data = await res.json();
    return normalizeServerBoard(data?.board ?? data);
  },

  saveBoard: async (username = "user", board: BoardData) => {
    const res = await fetch(`/api/board/${encodeURIComponent(username)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ board }),
    });
    if (!res.ok) throw new Error("Failed to save board");
    return await res.json();
  },
};

export const fetchBoard = API.fetchBoard;
export const saveBoard = API.saveBoard;

export const _normalizeServerBoard = normalizeServerBoard;

// Granular endpoints
export const createCard = async (
  username: string,
  columnId: string,
  card: { title: string; details?: string }
) => {
  const res = await fetch(`/api/board/${encodeURIComponent(username)}/cards`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ column_id: columnId, card }),
  });
  if (!res.ok) throw new Error("Failed to create card");
  return res.json();
};

export const deleteCard = async (username: string, cardId: string) => {
  const res = await fetch(`/api/board/${encodeURIComponent(username)}/cards/${cardId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete card");
  return res.json();
};

export const updateColumn = async (username: string, columnId: string, title: string) => {
  const res = await fetch(`/api/board/${encodeURIComponent(username)}/columns/${columnId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error("Failed to update column");
  return res.json();
};
