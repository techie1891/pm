# High level steps for project

## Part 1 – Plan (✅ Completed)
**Goal:** Turn the high‑level outline into a concrete, testable roadmap.

### Sub‑tasks (checklist)
- [x] Expand each part (2‑10) with detailed bullet‑point sub‑steps.
- [x] Add explicit **Success Criteria** for every sub‑step (e.g., "Docker container starts without errors").
- [x] Define **Unit / Integration Tests** that will verify each feature.
- [x] Create an `frontend/AGENTS.md` file that documents the existing frontend code base.
- [x] Review the enriched PLAN with the user and obtain approval.

### Success criteria
* All checklist items are ticked.
* The plan file contains a markdown table of parts, sub‑steps, and test expectations.
* `frontend/AGENTS.md` exists and accurately reflects the current components.

---

## Part 2 – Scaffolding (✅ In progress)
**Goal:** Provide a Docker‑based development environment that can serve a static page and expose a simple API.

### Sub‑tasks
- [ ] Verify `docker-compose.yml` builds the multi‑stage Dockerfile.
- [ ] Ensure `scripts/run` can start (`scripts/run start`) and stop (`scripts/run stop`) the container.
- [ ] Add a minimal **hello‑world** HTML page (`backend/public/index.html`).
- [ ] Confirm FastAPI mounts `public/` and serves the page at `http://localhost:8000/`.
- [ ] Verify `/api/hello` returns `{ "message": "hello" }`.

### Success criteria
* `docker compose up --build -d` completes without errors.
* Visiting `http://localhost:8000/` shows the hello‑world page.
* `curl http://localhost:8000/api/hello` returns the expected JSON.

---

## Part 3 – Add Frontend (⏳ Not started)
**Goal:** Build the Next.js app into static assets and serve them via FastAPI.

### Sub‑tasks
- [ ] Add a build script (`npm run export` or `next build && next export`).
- [ ] Update Dockerfile to copy the exported static folder into `backend/public/`.
- [ ] Verify the Kanban demo appears at `/` when the container runs.
- [ ] Write unit tests for React components (`vitest`/`@testing-library/react`).
- [ ] Write integration tests that start the container and request `/`.

### Success criteria
* After `docker compose up`, the root URL displays the Kanban board.
* All component tests pass (`npm test`).
* Integration test confirms HTTP 200 and board HTML.

---

## Part 4 – Fake User Sign‑in (⏳ Not started)
**Goal:** Guard the Kanban behind a dummy login (`user` / `password`).

### Sub‑tasks
- [ ] Add a login page (`frontend/src/components/LoginPage.tsx`).
- [ ] Store a simple session flag in a cookie or localStorage.
- [ ] Protect the protected route (`ProtectedBoard.tsx`) – redirect to login if not authenticated.
- [ ] Add a logout button that clears the session.
- [ ] Write end‑to‑end tests (Playwright) covering login, access, and logout.

### Success criteria
* Unauthenticated users see the login page.
* Correct credentials allow access to the Kanban.
* Logout returns the user to the login screen.
* All e2e tests pass.

---

## Part 5 – Database modeling (✅ Completed)
**Goal:** Persist each user's Kanban board in a lightweight SQLite database as JSON, expose simple CRUD API endpoints, and create migration/initialisation that runs automatically when the backend starts.

### Schema proposal
- Table: `boards`
	- `username` TEXT PRIMARY KEY — unique user identifier (for MVP a single hardcoded user will be used)
	- `board_json` TEXT NOT NULL — the Kanban board stored as a JSON string
	- `updated_at` TEXT NOT NULL — ISO timestamp of last update

### Sub‑tasks
- [x] Define schema and rationale (this file).
- [x] Add `docs/db_schema.md` with details and examples.
- [x] Implement DB initialisation on backend startup (`backend/main.py`).
- [x] Add endpoints: `GET /api/board/{username}` and `POST /api/board/{username}`.
- [x] Add backend unit tests to verify DB CRUD behavior (`backend/test_db.py`, `backend/test_crud.py`).
- [x] Add migration/seed logic (`migrate_board_shape()` in `backend/main.py`, `backend/seed.py`).

### Success criteria
- Backend creates `backend/kanban.db` if missing and the `boards` table exists (see `backend/main.py`).
- `GET /api/board/user` returns persisted or default board JSON (`GET /api/board/{username}`).
- `POST /api/board/user` stores the provided board JSON and returns an updated timestamp.

Implemented files/endpoints for Part 5:
- [backend/main.py](backend/main.py) — DB init, migrations, CRUD endpoints, granular card/column APIs, `apply-actions`.
- [backend/test_db.py](backend/test_db.py) and [backend/test_crud.py](backend/test_crud.py) — unit tests (all passing).
- [backend/seed.py](backend/seed.py) — optional seed data.

Status: Completed and validated via `pytest` inside the running container (10 tests passed).


## Part 6 – Backend (✅ Completed)
*Create CRUD API endpoints for the board and wire them to the SQLite DB.*

Implemented: full CRUD for cards and columns plus `apply-actions` in `backend/main.py`.

See: [backend/main.py](backend/main.py)

## Part 7 – Frontend ↔ Backend (✅ Completed)
*Connect the UI to the new API so the board persists.*

Implemented: API client and wiring in `frontend/src/lib/api.ts` and `frontend/src/components/KanbanBoard.tsx` with debounced saves and optimistic updates.

See: [frontend/src/lib/api.ts](frontend/src/lib/api.ts) and [frontend/src/components/KanbanBoard.tsx](frontend/src/components/KanbanBoard.tsx)

## Part 8 – AI connectivity (✅ Completed)
*Add a simple OpenRouter call to verify the AI client works.*

Implemented: `/api/ai/compute` in `backend/main.py` which proxies to OpenRouter when `OPENROUTER_API_KEY` is present, and otherwise provides a safe fallback evaluator/mock.

See: [backend/main.py](backend/main.py)

## Part 9 – AI‑driven Kanban (✅ Completed)
*Send board JSON + user prompt to the LLM, receive structured output, optionally update the board.*

Implemented: `/api/ai/modify-board` which requests JSON instructions from OpenRouter (when configured) or returns a mock action that adds a card. Server endpoint and `apply-actions` allow programmatic updates.

See: [backend/main.py](backend/main.py)

## Part 10 – AI Sidebar UI (✅ Completed)
*Build a chat sidebar that displays the conversation, forwards prompts to the backend, and refreshes the board on updates.*

Implemented: `frontend/src/components/AISidebar.tsx` and UI toggle in `KanbanBoard.tsx`. The sidebar sends prompts to `/api/ai/modify-board`, applies suggested `actions` via `/api/board/{username}/apply-actions`, and refreshes the board.

See: [frontend/src/components/AISidebar.tsx](frontend/src/components/AISidebar.tsx)