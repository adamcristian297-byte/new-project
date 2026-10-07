# Project Knowledge — read this first at session start

This is the single source of truth about this project for humans and AI agents.
Read it fully before making changes; keep it updated whenever the project evolves.

## 1. What this project is

- **Status:** brand new / greenfield. The workspace contains no application code yet.
- **Location:** `C:\Users\adamc\Desktop\freebuff` (Windows, Git Bash tooling).
- **Contents today:**
  - `knowledge.md` — this document.
  - `.freebuff/` — Freebuff agent metadata (`project-id`). Do not modify.
  - `.git/` — local git repository (initialized; see §3 for its state).
- **Stack:** not chosen yet. Do not assume a language or framework — check for a
  manifest first; if none exists, ask the user before scaffolding.

## 2. Where key code will live

To be filled in when the project is scaffolded. When adding code, record here:
main entry points, source directories, config files, and any generated/output dirs.

## 3. Git & GitHub workflow (important)

**Auto-commit policy — every AI session must follow this:**
- Commit **once per completed milestone** (a finished feature, fix, or refactor —
  not every intermediate step).
- Never leave a completed milestone uncommitted if the user is waiting on it.
- Write meaningful messages: what changed and why, not "update".
- **Do not commit:** secrets, credentials, `.env` files, `node_modules/`,
  editor/OS junk. Check `git status` output carefully before staging; stage files
  explicitly (avoid `git add -A` in large repos).

**Current repo state (as of 2026-10-07):**
- `git init` done; default branch `master`.
- **No commits yet** and **no remote configured**.
- **Blocker 1 — identity:** `user.name` / `user.email` are not set (user chose to
  defer). Commits will fail with "unable to auto-detect author" until this is fixed:
  ```
  git config user.name "Your Name"
  git config user.email "you@users.noreply.github.com"
  ```
- **Blocker 2 — remote:** no `gh` CLI and no stored GitHub credentials on this
  machine. User will provide a repo URL; then:
  ```
  git remote add origin <REPO_URL>
  git push -u origin master
  ```
  First push will trigger Git Credential Manager's login popup (interactive — not
  runnable headlessly by the agent). After that, pushing works with stored creds.
- **Pushing** requires the user's explicit request per session; the milestone
  commits themselves are pre-authorized by the user.

## 4. Commands

None yet — no `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, or Makefile
exists. When tooling is added, record the real commands here from the manifest
(install / dev / test / lint / build), e.g. `npm install`, `npm run dev`.

## 5. Conventions & gotchas

- **Not a stack-free zone:** always inspect for manifests before assuming tooling.
- **Windows environment:** commands run via Git Bash; use POSIX syntax.
- **`.freebuff/` is off-limits** for edits.
- **This file is read at AI session init** — keep it current so the next session
  needs zero onboarding. Update sections 1–4 the moment they change.
- Interactive commands (credential popups, `gh auth login`) must be handed to the
  user, not automated.
