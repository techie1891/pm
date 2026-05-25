"use client";

import { useState } from "react";
import { saveBoard } from "@/lib/api";

type Props = {
  board: any;
  onBoardChange: (board: any) => void;
};

export const AISidebar = ({ board, onBoardChange }: Props) => {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [last, setLast] = useState<any>(null);

  const handleSend = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/ai/modify-board`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, board }),
      });
      const data = await res.json();
      setLast(data);
      // If AI returned actions, apply them via server action endpoint
      if (data.suggested && data.suggested.actions) {
        const actionsRes = await fetch(`/api/board/user/apply-actions`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ actions: data.suggested.actions }),
        });
        const actionsData = await actionsRes.json();
        if (actionsData.board) {
          onBoardChange(actionsData.board);
          saveBoard("user", actionsData.board).catch(() => {});
        }
      } else if (data.ok && data.board) {
        onBoardChange(data.board);
        saveBoard("user", data.board).catch(() => {});
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <aside className="w-80 border-l border-[var(--stroke)] bg-white p-4">
      <h3 className="font-semibold">AI Assistant</h3>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Ask the AI to update the board, e.g. 'Add a card to the backlog about pricing'"
        className="w-full h-32 rounded-md border p-2"
      />
      <div className="mt-2 flex gap-2">
        <button
          onClick={handleSend}
          disabled={loading || !prompt.trim()}
          className="rounded bg-[var(--primary-blue)] px-3 py-2 text-white"
        >
          {loading ? "Working..." : "Send"}
        </button>
      </div>
      <div className="mt-4 text-sm">
        <pre className="whitespace-pre-wrap">{last ? JSON.stringify(last, null, 2) : ""}</pre>
      </div>
    </aside>
  );
};
