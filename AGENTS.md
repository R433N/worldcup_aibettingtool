# AGENTS.md

## Project overview

`worldcup_aibettingtool` is a soccer World Cup betting **value analytics**
platform. A Python/FastAPI backend fits a Dixon-Coles match model, removes
bookmaker vig, and computes expected value + fractional-Kelly stakes; a
React+Vite+TS frontend visualises value bets, fixtures, and team ratings.

- Backend: `backend/` (Python, FastAPI, NumPy/SciPy). Source in `backend/app`,
  tests in `backend/tests`.
- Frontend: `frontend/` (React 19, Vite, TypeScript).

The statistical engine lives in `backend/app/stats` and is pure/framework-free;
prefer adding model logic there and keeping `services`/`api` thin. Data access
is behind repository protocols in `backend/app/infrastructure` — swap the CSV
repos for a real feed without touching the model.

## Cursor Cloud specific instructions

Standard commands live in `README.md`; the notes below are the non-obvious bits.

- **Backend runs in a virtualenv at `backend/.venv`** (system pip is
  externally-managed, so a venv is required). Activate it before any backend
  command: `cd backend && . .venv/bin/activate`. The update script (re)creates
  and populates this venv.
- **Run the backend before the frontend.** The Vite dev server proxies `/api/*`
  to `http://localhost:8000` (see `frontend/vite.config.ts`); without the
  backend up, the dashboard shows load errors. Override the target with the
  `VITE_API_TARGET` env var if the backend is on another host/port.
- **Sample data is generated, not hand-written, and is committed.** It is
  *synthetic* (deterministic seed). Regenerate with
  `cd backend && . .venv/bin/activate && python -m scripts.generate_sample_data`.
  The match results are sampled from a *known* Dixon-Coles process, so
  `tests/test_dixon_coles.py::test_recovers_known_parameters` and the
  ratings-ordering API test assume those ground-truth strengths (Brazil is the
  strongest team). If you change the generator's parameters or sample size,
  expect to update those tests.
- **The model is fit once per process and cached** (`ModelService`, wired via a
  cached `Container` in `app/api/deps.py`). Fitting is an MLE optimisation
  (~1-2s). If you change `app/data/*.csv` while the server is running, restart it
  (or call `ModelService.refit`) — the cached fit will not pick up new data.
- **Checks**: backend `ruff check . && mypy app && pytest` (from `backend/`,
  venv active); frontend `npm run lint && npm run build` (from `frontend/`).
- Running services in this environment: backend on `:8000`
  (`uvicorn app.main:app --reload`), frontend on `:5173` (`npm run dev`).
