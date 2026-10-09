# StockPilot — Project Knowledge (read this first at AI session start)

Single source of truth for humans and AI agents. Keep it updated as the project evolves.

## 1. What this project is

**StockPilot** — an AI-powered strategy-based stock trading platform, built from a
detailed phased spec. Users describe trading strategies in plain English; an LLM
parses them into structured rules; users review/edit, backtest, and run them in
paper trading. Live trading (Alpaca) is optional Phase 6, gated behind typed consent.

**Core loop:** Describe → Parse (LLM, tool-calling) → Review/Edit → Backtest → Paper Trade → (optional) Live

**Non-negotiable principles:**
- Paper trading is the default; live requires explicit typed consent.
- Risk limits are enforced by a deterministic server-side engine — never AI, never frontend.
- The AI never executes trades, moves funds, or holds credentials; it only emits
  schema-validated tool-call objects (`submit_strategy_rules`, `request_clarification`,
  read-only copilot tools). Never execute LLM-generated code.
- Stack is 100% free: SQLite + yfinance + free/local LLM. Total $0/month.
- Row-centred spec source: the full spec is in this conversation (sections 1–12 with build order); treat [knowledge.md](knowledge.md) as the condensed operational memory.

## 2. Layout

```
backend/   FastAPI + SQLAlchemy(async, SQLite/aiosqlite) + Pydantic v2  (uv, Python 3.12)
backend/app/llm/          provider registry + universal OpenAI-compatible adapter
backend/app/main.py       FastAPI app, /health echoes active provider (no secrets)
backend/tests/            pytest (16 passing); never hit the network in tests
frontend/  Next.js 14 App Router + TS + Tailwind + shadcn plan            (pnpm)
.github/、docs/: reserved; alembic migrations land in Phase 1 (backend/alembic/)
```

## 3. Commands

Backend (from `backend/`, needs `uv` on PATH: `~/.local/bin` on this machine):
- `uv sync` — install deps (Python 3.12.15 pinned via `.python-version`)
- `uv run pytest` — tests (16 passing, coverage in app/)
- `uv run ruff check . --fix` / `uv run ruff format .` — lint/format
- `uv run mypy app` — strict typecheck
- `uv run uvicorn app.main:app --port 8200 --reload` — dev server; health:
  `curl http://127.0.0.1:8200/health` -> {status, version, llm:{provider, model, key_state}}

Frontend (from `frontend/`; pnpm shim is broken in Git Bash — ALWAYS use the
`.cmd` wrapper: `PNPM="$(cygpath -u "$APPDATA")/npm/pnpm.cmd"; "$PNPM" ...`):
- `pnpm dev` — dev server (Next 14, port 3000)
- `pnpm test` — vitest (jsdom; config in vitest.config.ts)
- `pnpm lint` — ESLint; `pnpm build` — prod build (verified green)

## 4. Environment & stack decisions

- `.env` lives at repo **root** (backend reads it via `parents[2]` in
  `app/config.py`); see [.env.example](.env.example) for every key. Never commit `.env`.
- LLM providers (OpenAI-compatible adapter, `LLM_PROVIDER` selects):
  gemini (default: `gemini-2.5-flash`, key from aistudio.google.com — free),
  groq (`llama-3.3-70b-versatile`, free key),
  ollama (local `qwen2.5:7b`, zero keys, `OLLAMA_BASE_URL=http://localhost:11434/v1`).
- Missing key = loud `LLMNotConfiguredError` from the adapter — never guess rules.
- Data: yfinance (keyless, unofficial — cache hard: ≥60s quotes, ≥1d history;
  fixture CSVs in tests, never live calls). Alpaca stays optional Phase 6 only.
- Scheduler = APScheduler in-process; cache = cachetools; no Celery/Redis anywhere.

## 5. Build order & status (wait for user approval between phases)

- [x] **Phase 0** — repo scaffold, tooling (ruff/mypy/pytest/vitest/ESLint), LLM adapter,
      `/health`, test skeleton, .env.example, .gitignore. Backend commits: `2a773ff`,
      `9ae3019`; frontend: `38bb84d`; docs: `699c495`, `37ab939`.
- [ ] **Phase 1** — DB models + Alembic + JWT auth + refresh rotation.
- [ ] **Phase 2** — market data service (yfinance, cachetools, ticker validation).
- [ ] **Phase 3** — strategy parser (tool calling; system prompt is spec section 6,
      embed verbatim, temperature 0) + Strategy Builder UI + versioning.
- [ ] **Phase 4** — deterministic backtester (bar-close-only, no lookahead,
      determinism test) + report UI + SMA crossover regression on fixture data.
- [ ] **Phase 5** — paper trading + risk engine + APScheduler + dashboard + ntfy/Telegram.
- [ ] **Phase 6 (only if user asks)** — Alpaca live, kill switch, shadow mode.
- [ ] **Phase 7** — audit log UI, Playwright E2E, README.

## 6. Git & GitHub workflow

- Remote: `origin` → `https://github.com/adamcristian297-byte/new-project.git` (master).
- Identity (repo-local): `adamcristian297-byte` <adamcristian297-byte@users.noreply.github.com>.
- **Auto-commit rule:** commit once per completed milestone (finished feature/fix,
  not intermediate steps); meaningful messages; push succeeds (credentials stored).
- Never commit: `.env`, keys, `__pycache__`, `node_modules`, `.next`, `*.db`
  (root `.gitignore` covers these — a cache slipped into `2a773ff` and was purged in
  `9ae3019`; stay careful).
- Stage explicitly (`git add backend/ app/files`), avoid bare `git add -A` on shares.

## 7. Gotchas (read before debugging)

- **pnpm in Git Bash is broken** (npm shim mangles paths) → always use the `.cmd`
  wrapper shown in §3. `uv`/`uvx` live in `~/.local/bin` — export PATH first in new shells.
- Freebuff sessions **kill background servers** between turns — restart uvicorn/vite
  yourself and re-verify; never assume a server survived.
- Python was extended to 3.14 by default at one point; `backend/.python-version`
  pins 3.12 — do not remove it.
- yfinance is unofficial: every call needs error handling + cache; never in tests.
- Windows/Git Bash: use POSIX syntax; expect CRLF warnings (harmless).
- `.freebuff/` is agent metadata — leave it untracked and untouched.
