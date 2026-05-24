# Frontend AGENTS.md

This file documents the current state of the **frontend** Next.js application located in `frontend/`.

## Project structure
```
frontend/
├─ src/
│  ├─ app/
│  │  ├─ globals.css
│  │  ├─ layout.tsx          # Root layout for the Next.js app
│  │  └─ page.tsx            # Home page – currently renders the demo Kanban board
│  └─ components/
│     ├─ KanbanBoard.tsx      # Main board component; renders columns and cards
│     ├─ KanbanColumn.tsx     # Column component – handles column title and drag‑drop area
│     ├─ KanbanCard.tsx       # Card component – displays card title, description, and edit UI
│     ├─ KanbanCardPreview.tsx# Small preview used during drag‑and‑drop
│     ├─ NewCardForm.tsx      # Form for creating a new card in a column
│     ├─ LoginPage.tsx        # Login screen (currently a placeholder – will be expanded in Part 4)
│     └─ ProtectedBoard.tsx   # Wrapper that will enforce authentication (future work)
│  └─ lib/
│     ├─ auth.tsx            # Simple auth helper (hard‑coded credentials for MVP)
│     └─ kanban.ts            # Client‑side utilities for board manipulation (currently in‑memory)
└─ test/
   ├─ setup.ts               # Global test setup for Vitest
   └─ vitest.d.ts            # Type definitions for Vitest
```

## Key components
* **KanbanBoard.tsx** – Renders a list of `KanbanColumn` components. Uses `react-beautiful-dnd` (or similar) for drag‑and‑drop.
* **KanbanColumn.tsx** – Displays a column title (editable) and a list of `KanbanCard` components.
* **KanbanCard.tsx** – Shows card details and provides an edit button that opens a modal.
* **LoginPage.tsx** – Simple login UI; currently not wired to any backend authentication.
* **ProtectedBoard.tsx** – Wrapper component that will later check authentication before rendering `KanbanBoard`.

## Tests
* Unit tests exist for most components under `src/components/*.test.tsx` using Vitest and React Testing Library.
* Integration tests are located in `test/` and are executed via the `npm test` script.

## Future work (refer to `docs/PLAN.md`)
* Implement real authentication flow (Part 4).
* Connect the board to the FastAPI backend API (Part 7).
* Add AI chat sidebar (Part 10).

---

*This file is generated automatically as part of the implementation plan.*