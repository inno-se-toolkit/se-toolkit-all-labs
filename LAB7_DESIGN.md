# Lab 7 — Build a Client with an AI Coding Agent

## Concept

Students use an AI coding agent (Qwen Code) to build a Telegram bot client
for the LMS backend they deployed in Labs 5–6.

The lab teaches how to collaborate with an AI agent as a development partner:
plan, scaffold, build iteratively, debug with agent assistance, and deliver
a working product connected to a real backend.

## Prerequisites

- Labs 2–6 completed (backend deployed on VM with PostgreSQL, ETL, analytics)
- Student's LMS backend running at `http://<VM_IP>:8000`
- Working API key for the backend (`LMS_API_KEY`)
- Telegram bot token (from @BotFather)

### SSH Setup (carried over from Lab 6 Task 3)

In Lab 6 Task 3, students added the autochecker SSH public key to their
**own user's** `~/.ssh/authorized_keys` and registered their `vm_username`
with the bot. Lab 7 relies on this same setup — the autochecker SSHes as
the student's main user for all runtime checks.

**Lab 7 setup must verify this is still in place.** If a student skipped
Lab 6 Task 3 or reinstalled their VM, they need to redo it:

```bash
# On their VM, as their main user:
mkdir -p ~/.ssh
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKiL0DDQZw7L0Uf1c9cNlREY7IS6ZkIbGVWNsClqGNCZ se-toolkit-autochecker' >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
```

The bot already stores `vm_username` from Lab 6. If missing, the lab setup
task should prompt the student to register it (same flow as Lab 6 Task 3:
run `whoami`, reply to the bot).

## Learning Outcomes

1. Use an AI coding agent to plan and implement a client application
2. Design a testable handler architecture (logic separated from transport)
3. Connect a client to an existing REST API with authentication
4. Debug integration issues iteratively with agent assistance
5. Deploy a multi-service system (backend + bot) on a remote VM

---

## Verification Model

> No `clone_and_run`. No separate `autochecker` SSH user.
> Two verification channels: **GitHub API** for code, **SSH** for deployment.
>
> **Structural checks → GitHub API**
> File existence, word counts, regex matches — same as Labs 1–6.
> We know the student's GitHub alias and repo name, so this works out of the box.
>
> **Runtime & deployment checks → SSH as student's main user**
> SSHes to the student's VM as their main user (`vm_username`).
> Runs `python bot.py --test`, `docker ps`, `curl`, etc.
> All checks see the real environment — real backend, real `.env`, real Docker.
>
> **Repo integrity check → SSH**
> Verify that the deployed code on the VM actually comes from the student's
> GitHub repo. SSH in, run `git -C <project-dir> remote get-url origin`,
> and confirm it matches `github.com/{alias}/{repo-name}`.
> This prevents students from deploying someone else's code.
>
> **Implications:**
> - `--test` mode hits the **real backend on localhost** — no mock client needed
> - If the backend is down, `/health` should report it as down (correct behavior)
> - Student must have their repo cloned and their code deployed on the VM
>
> **Project directory discovery:** Autochecker looks for `~/lab-07-*` or the
> repo name from the spec. Fallback: search home dir for `bot.py`/`main.py`.

---

## Prioritized Requirements

### P0 — Must Have

1. Project builds and starts without errors
2. Testable handler layer — handlers callable without Telegram
3. CLI test mode: `python bot.py --test "/command"` prints response to stdout
4. `/start` — welcome message with bot description
5. `/help` — lists all available commands with descriptions
6. `/health` — calls backend `GET /items`, reports up/down status
7. At least 2 data commands that fetch real data from the LMS backend
8. README with: what the bot does, how to install, how to configure, how to run

### P1 — Should Have

1. `/ask <question>` — answers questions about the LMS using an LLM
2. Inline keyboard buttons or reply menu for main commands
3. Periodic health check (configurable interval, logs or sends alert on failure)
4. Graceful error handling (backend down → user-friendly message, not crash)

### P2 — Nice to Have

1. Rich message formatting (tables, charts as images)
2. Admin-only commands (e.g., trigger ETL sync, view system stats)
3. Response caching for expensive queries
4. Conversation context for `/ask` (multi-turn)

---

## Task Breakdown

### Setup

**Goal:** Ensure the student's VM is reachable, the repo exists, and the
backend is running. Same pattern as Labs 2–6 setup tasks.

**What students do:**
1. Ensure SSH key is in `~/.ssh/authorized_keys` (from Lab 6 Task 3)
2. Register `vm_username` with the bot (if not already done)
3. Create the lab repo on GitHub
4. Confirm their LMS backend is running on the VM

**Auto-checks:**

| ID | Check | Channel | How |
|----|-------|---------|-----|
| setup-repo | Repository exists on GitHub | GitHub | repo_exists |
| setup-ssh | SSH connectivity — can log in as student's main user | SSH | `echo ok` via SSH as `vm_username` |
| setup-backend | LMS backend is running | SSH | `curl -sf http://localhost:8000/items` returns 200 |

### Task 1 — Plan and Scaffold

**Goal:** Use Qwen Code to create a development plan and project skeleton.

**What students do:**
1. Give the prioritized requirements to Qwen Code
2. Ask it to produce an implementation plan
3. Ask it to scaffold the project
4. Verify the scaffold runs

**Deliverables:**
- `PLAN.md` — development plan produced with agent assistance
- Project structure with separated handler layer
- `requirements.txt` or `pyproject.toml` with dependencies
- `.env.example` with required variables
- Entry point (`bot.py` or `main.py`) that starts without crashing
- CLI test mode wired up (even if handlers return placeholder text)

**Auto-checks:**

| ID | Check | Channel | How |
|----|-------|---------|-----|
| t1-plan | `PLAN.md` exists and has ≥100 words | GitHub | file_exists + file_word_count |
| t1-env | `.env.example` exists with `BOT_TOKEN`, `LMS_API_URL`, `LMS_API_KEY` | GitHub | file_exists + regex_in_file |
| t1-readme | `README.md` exists and has ≥150 words | GitHub | file_exists + file_word_count |
| t1-deps | `requirements.txt` or `pyproject.toml` exists | GitHub | file_exists |
| t1-handlers | Handler module exists separately from bot entry point | GitHub | file_exists — check for `handlers.py` or `handlers/` |
| t1-install | Dependencies install without errors | SSH | `pip install -r requirements.txt` on VM |
| t1-test-mode | `python bot.py --test "/start"` exits 0 and produces output | SSH | check exit code + stdout non-empty |

### Task 2 — Backend Integration

**Goal:** Connect the bot to the student's LMS backend with real data commands.

**What students do:**
1. Implement `/health` that calls `GET /items` on their backend
2. Implement at least 2 data commands (suggested below)
3. Handle backend errors gracefully
4. Test locally, then against their deployed backend

**Suggested data commands** (students pick 2+):

| Command | Backend endpoint | What it shows |
|---------|-----------------|---------------|
| `/labs` | `GET /items` | List of available labs |
| `/scores <lab>` | `GET /analytics/pass-rates?lab=` | Per-task pass rates |
| `/timeline <lab>` | `GET /analytics/timeline?lab=` | Submissions over time |
| `/groups <lab>` | `GET /analytics/groups?lab=` | Per-group performance |
| `/top [lab] [N]` | `GET /analytics/top-learners?lab=&limit=` | Top N learners |
| `/learners` | `GET /learners` | Enrolled learner count/list |
| `/sync` | `POST /pipeline/sync` | Trigger ETL, show result |

**Auto-checks:**

| ID | Check | Channel | How |
|----|-------|---------|-----|
| t2-start | `--test "/start"` returns text containing "welcome" or bot name (case-insensitive) | SSH | regex on stdout |
| t2-help | `--test "/help"` output lists at least 4 commands | SSH | count `/command` patterns in stdout |
| t2-health | `--test "/health"` output contains "healthy" or "ok" or status indicator | SSH | hits real backend on localhost |
| t2-data-1 | `--test "/labs"` (or first data command) returns non-empty structured output | SSH | stdout has ≥2 lines |
| t2-data-2 | `--test` with second data command returns non-empty output | SSH | stdout non-empty |
| t2-error | Backend error produces user-friendly message, not traceback | SSH | stop backend → `--test "/health"` → no `Traceback` → restart |

> `--test` mode hits the real backend on localhost. No mock needed.

### Task 3 — Smart Interaction

**Goal:** Add an LLM-powered `/ask` command and interactive UX elements.

**What students do:**
1. Implement `/ask <question>` that answers questions about the LMS data
2. The `/ask` handler should fetch relevant backend data, then pass it
   to an LLM with context for a natural language answer
3. Add inline keyboard buttons or a reply keyboard for common commands
4. (P1) Add periodic health check with configurable interval

**How `/ask` works:**
```
User: /ask which lab has the lowest pass rate?
Bot:  → calls GET /analytics/pass-rates for each lab
      → sends data + question to LLM (via OpenRouter or similar)
      → returns formatted answer
```

This connects to Lab 6 (LLM integration) — students reuse the pattern
of "fetch data → build prompt → call LLM → format response."

**Auto-checks:**

| ID | Check | Channel | How |
|----|-------|---------|-----|
| t3-ask | `--test "/ask what labs are available"` returns non-empty answer (≥20 chars) | SSH | real LLM key + real backend from student's `.env` |
| t3-buttons | Source code contains keyboard/button setup (InlineKeyboardMarkup, ReplyKeyboardMarkup, or equivalent) | GitHub | regex_in_file |
| t3-ask-data | `/ask` handler fetches from backend before calling LLM (not pure LLM) | GitHub | regex_in_file — look for API call in ask handler |

> `/ask` runs with the student's own `.env` on their VM. If the key is
> missing or expired, the check fails — student's responsibility.

### Task 4 — Deploy and Document

**Goal:** Deploy the bot on the student's VM alongside the backend.

**What students do:**
1. Add the bot to their existing `docker-compose.yml` (or create one)
2. Bot runs as a separate service, connects to the backend via Docker network
3. Verify the bot responds in Telegram
4. Update README with deployment instructions

**Auto-checks:**

| ID | Check | Channel | How |
|----|-------|---------|-----|
| t4-repo-match | Deployed code is from student's GitHub repo | SSH | `git remote get-url origin` matches `github.com/{alias}/{repo}` |
| t4-compose | `docker-compose.yml` (or `compose.yaml`) includes a bot service | SSH | `grep -i bot docker-compose.yml` |
| t4-running | Bot container is running | SSH | `docker ps` shows bot container |
| t4-health | Backend is still up alongside the bot | SSH | `curl -sf http://localhost:8000/items` returns 200 |
| t4-readme | README has "deploy" section | GitHub | regex_in_file — heading containing "deploy" |

**TA verification (demo):**
- Bot responds to `/start`, `/help`, `/health` in Telegram
- At least 2 data commands return real backend data
- `/ask` returns a meaningful answer
- Student explains how they used Qwen Code during development
- Student can explain the handler architecture

---

## Verification Strategy

### Auto-Checked (autochecker)

**GitHub API** — structural checks on the repo (file existence, content, regex):

**SSH as student's main user** — runtime & deployment checks on the VM:

**Setup (3 checks)**
- GitHub: repo exists
- SSH: connectivity (prerequisite for all SSH checks), backend running

**Task 1 — Structure & Scaffold (7 checks)**
- GitHub: PLAN.md, .env.example, README.md, deps file, handler module
- SSH: dependencies install, `--test "/start"` works

**Task 2 — Backend Integration (6 checks)**
- SSH: /start, /help return expected content via test mode
- SSH: /health returns status (real backend on localhost)
- SSH: 2 data commands return output (real backend data)
- SSH: error handling (no traceback on failure)

**Task 3 — Smart Features (3 checks)**
- SSH: /ask returns non-empty answer (real LLM key from student's .env)
- GitHub: button/keyboard code exists, /ask handler includes API fetch

**Task 4 — Deployment (5 checks)**
- SSH: repo integrity — deployed code matches student's GitHub repo
- SSH: compose file has bot service, bot container running, backend healthy
- GitHub: README has deploy section

**Total: ~24 auto-checks (3 setup + 7 + 6 + 3 + 5)**

### TA-Verified (demo)

- Live Telegram interaction
- Real backend data flowing through bot
- `/ask` quality and relevance
- Code walkthrough: handler architecture
- Development process: how Qwen Code was used
- Interaction quality and usability

---

## Test Mode Specification

The bot must support a `--test` flag for offline command verification:

```bash
# Syntax
python bot.py --test "<command> [args]"

# Examples
python bot.py --test "/start"
python bot.py --test "/help"
python bot.py --test "/health"
python bot.py --test "/labs"
python bot.py --test "/ask what labs are available"
```

**Behavior:**
- Prints the bot's response text to **stdout**
- Hits the **real backend on localhost** (reads `LMS_API_URL` from `.env`)
- Exits with code **0** on success, **non-zero** on error
- Does NOT connect to Telegram (no `BOT_TOKEN` required)
- LLM-dependent commands (`/ask`) use the real `OPENROUTER_API_KEY` from `.env`

**Why this matters:**
- Autochecker can verify handler logic without Telegram
- Forces students to separate handlers from transport (good architecture)
- Makes development faster (test without deploying to Telegram)

**Implementation hint for students:**

```python
# bot.py (simplified)
import sys
from handlers import handle_command
from api_client import ApiClient

if __name__ == "__main__":
    if "--test" in sys.argv:
        command = sys.argv[sys.argv.index("--test") + 1]
        client = ApiClient()  # reads LMS_API_URL from .env
        print(handle_command(command, client))
    else:
        # normal Telegram bot startup
        ...
```

---

## Architecture Guidance (given to students)

```
bot.py              ← entry point (Telegram startup OR --test mode)
handlers/
  start.py          ← /start, /help
  health.py         ← /health, periodic check
  data.py           ← /labs, /scores, /top, etc.
  ask.py            ← /ask (LLM-powered)
services/
  api_client.py     ← HTTP client for LMS backend
  llm.py            ← LLM integration (OpenRouter)
config.py           ← env var loading
.env.example
requirements.txt
README.md
PLAN.md
docker-compose.yml  ← or added to existing compose
Dockerfile
```

Students don't have to follow this exactly — it's a suggestion. The only
hard requirement is that handlers are testable without Telegram.

---

## Scoring

| Task | Weight | Notes |
|------|--------|-------|
| Task 1 — Plan & Scaffold | 20% | Mostly structural checks |
| Task 2 — Backend Integration | 35% | Core functionality |
| Task 3 — Smart Features | 25% | /ask + UX |
| Task 4 — Deploy & Document | 20% | Deployment + README |

Pass threshold: 75% (consistent with other labs)

---

## Open Questions

1. **Should we provide a bot template repo?** Or start from empty repo?
   - Pro template: less boilerplate friction, students focus on integration
   - Pro empty: more realistic "start from scratch with agent" experience
   - **Leaning toward:** empty repo with only README containing requirements.
     The whole point is that Qwen scaffolds it.

2. **Periodic health check verification:**
   - Hard to auto-check a background task
   - Could require a `--test-healthcheck` flag that runs one cycle and exits
   - **Leaning toward:** P1 (should have), TA-verified in demo

## Resolved Decisions

- **Verification model:** GitHub API for structural checks, SSH for runtime.
  No `clone_and_run`. No `autochecker` SSH user.
- **SSH user:** Always SSH as the student's main user (`vm_username`).
  This gives access to repo, Docker, `.env`, everything.
- **Repo integrity:** `git remote get-url origin` on VM must match the
  student's known GitHub alias + repo name. Prevents deploying others' code.
- **Mock client:** Not needed. Checks run on the student's VM where the
  real backend is on localhost. `--test` mode hits the real API.
- **LLM API key:** Runs with student's own `.env` on their VM. If key is
  missing, check fails — student's responsibility.
- **Docker network:** Single compose file with bot + backend on the same
  network. Bot reaches backend via Docker service name.
- **Project directory:** Convention `~/lab-07-*` or repo name from spec.
  Fallback: search home dir for entry point with `--test` flag.
