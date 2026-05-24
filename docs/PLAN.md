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

## Part 5 – Database modeling (⏳ Not started)
*Propose a SQLite schema that stores a JSON representation of each user's board.*

## Part 6 – Backend (⏳ Not started)
*Create CRUD API endpoints for the board and wire them to the SQLite DB.*

## Part 7 – Frontend ↔ Backend (⏳ Not started)
*Connect the UI to the new API so the board persists.*

## Part 8 – AI connectivity (⏳ Not started)
*Add a simple OpenRouter call (`2+2`) to verify the AI client works.*

## Part 9 – AI‑driven Kanban (⏳ Not started)
*Send board JSON + user prompt to the LLM, receive structured output, optionally update the board.*

## Part 10 – AI Sidebar UI (⏳ Not started)
*Build a chat sidebar that displays the conversation, forwards prompts to the backend, and refreshes the board on updates.*