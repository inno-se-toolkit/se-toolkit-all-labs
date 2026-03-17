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

## Learning Outcomes

1. Use an AI coding agent to plan and implement a client application
2. Design a testable handler architecture (logic separated from transport)
3. Connect a client to an existing REST API with authentication
4. Debug integration issues iteratively with agent assistance
5. Deploy a multi-service system (backend + bot) on a remote VM

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

| ID | Check | Type | How |
|----|-------|------|-----|
| t1-plan | `PLAN.md` exists and has ≥100 words | file_exists + file_word_count | structural |
| t1-env | `.env.example` exists with `BOT_TOKEN`, `LMS_API_URL`, `LMS_API_KEY` | file_exists + regex_in_file | structural |
| t1-readme | `README.md` exists and has ≥150 words | file_exists + file_word_count | structural |
| t1-deps | `requirements.txt` or `pyproject.toml` exists | file_exists | structural |
| t1-handlers | Handler module exists separately from bot entry point | file_exists | structural — check for `handlers.py` or `handlers/` dir |
| t1-install | `pip install -r requirements.txt` succeeds | clone_and_run | run in venv |
| t1-test-mode | `python bot.py --test "/start"` exits 0 and produces output | clone_and_run | check exit code + stdout non-empty |

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

| ID | Check | Type | How |
|----|-------|------|-----|
| t2-start | `--test "/start"` returns text containing "welcome" or bot name (case-insensitive) | clone_and_run | regex on stdout |
| t2-help | `--test "/help"` output lists at least 4 commands | clone_and_run | count `/command` patterns in output |
| t2-health | `--test "/health"` output contains "healthy" or "ok" or status indicator | clone_and_run | needs mock or real backend; see note below |
| t2-data-1 | `--test "/labs"` (or first data command) returns non-empty structured output | clone_and_run | stdout has ≥2 lines or JSON-like content |
| t2-data-2 | `--test` with second data command returns non-empty output | clone_and_run | stdout non-empty |
| t2-error | `--test "/health"` with no backend returns error message, not traceback | clone_and_run | run without backend env; check no `Traceback` in stderr |

> **Note on backend-dependent checks:** For `clone_and_run` checks, the
> autochecker won't have access to the student's live backend. Two options:
>
> **Option A — Mock mode:** Require `--test` mode to use a built-in mock
> API client that returns sample data. This tests handler logic without a
> real backend. The mock should be part of the student's codebase.
>
> **Option B — Live VM check:** Use SSH to the student's VM and run
> `curl` against the bot's test endpoint. This verifies real integration
> but requires the bot to be deployed (Task 4).
>
> **Recommendation:** Use Option A for Task 2 checks (handler logic),
> Option B for Task 4 checks (deployment verification).

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

| ID | Check | Type | How |
|----|-------|------|-----|
| t3-ask | `--test "/ask what labs are available"` returns non-empty answer (≥20 chars) | clone_and_run | needs LLM API key in env or mock |
| t3-buttons | Source code contains keyboard/button setup (InlineKeyboardMarkup, ReplyKeyboardMarkup, or equivalent) | regex_in_file | grep handler code |
| t3-ask-data | `/ask` handler fetches from backend before calling LLM (not pure LLM) | code review / regex | look for API call in ask handler path |

> **Note:** `/ask` checks are hard to fully auto-verify since they depend on
> an LLM API key. Options:
> - Require `OPENROUTER_API_KEY` in `.env.example` and test with a real key
> - Accept that `/ask` is partly TA-verified
> - Check that the handler code path includes both an API fetch and an LLM call

### Task 4 — Deploy and Document

**Goal:** Deploy the bot on the student's VM alongside the backend.

**What students do:**
1. Add the bot to their existing `docker-compose.yml` (or create one)
2. Bot runs as a separate service, connects to the backend via Docker network
3. Verify the bot responds in Telegram
4. Update README with deployment instructions

**Auto-checks (via SSH to student VM):**

| ID | Check | Type | How |
|----|-------|------|-----|
| t4-compose | `docker-compose.yml` (or `compose.yaml`) includes a bot service | SSH + grep | check compose file on VM |
| t4-running | Bot container is running | SSH | `docker ps` shows bot container |
| t4-health | `curl http://localhost:8000/items` from VM returns 200 | SSH | verify backend is still up |
| t4-readme | README has "deploy" section (case-insensitive heading) | file_exists + regex_in_file | structural |

**TA verification (demo):**
- Bot responds to `/start`, `/help`, `/health` in Telegram
- At least 2 data commands return real backend data
- `/ask` returns a meaningful answer
- Student explains how they used Qwen Code during development
- Student can explain the handler architecture

---

## Verification Strategy

### Auto-Checked (autochecker)

**Task 1 — Structure & Scaffold (7 checks)**
- File existence: PLAN.md, .env.example, README.md, deps file, handler module
- Install: dependencies install cleanly
- Test mode: `--test "/start"` works

**Task 2 — Backend Integration (6 checks)**
- /start, /help return expected content via test mode
- /health returns status (with mock)
- 2 data commands return output (with mock)
- Error handling (no traceback on failure)

**Task 3 — Smart Features (3 checks)**
- /ask returns non-empty answer
- Button/keyboard code exists
- /ask handler includes API fetch

**Task 4 — Deployment (4 checks)**
- Compose file has bot service
- Bot container running on VM
- Backend still healthy
- README has deploy section

**Total: ~20 auto-checks**

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
- Uses a **mock API client** (no real backend needed) for data commands
- Exits with code **0** on success, **non-zero** on error
- Does NOT connect to Telegram (no BOT_TOKEN required)
- LLM-dependent commands (`/ask`) may use a real API key if available,
  or return a placeholder response if not

**Why this matters:**
- Autochecker can verify handler logic without Telegram or a live backend
- Forces students to separate handlers from transport (good architecture)
- Makes development faster (test without deploying)

**Implementation hint for students:**

```python
# bot.py (simplified)
import sys
from handlers import handle_command
from api_client import MockClient, RealClient

if __name__ == "__main__":
    if "--test" in sys.argv:
        command = sys.argv[sys.argv.index("--test") + 1]
        client = MockClient()  # no real backend needed
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
  api_client.py     ← real HTTP client for LMS backend
  mock_client.py    ← mock client for --test mode
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

2. **Mock client: provided or student-built?**
   - If provided: consistent test interface, easier auto-checking
   - If student-built: teaches mocking, but adds scope
   - **Leaning toward:** student-built, but with clear spec of what mock
     should return (sample data in the lab handout)

3. **LLM API key for `/ask`:**
   - Students already have OpenRouter keys from Lab 6
   - Autochecker needs a key to verify `/ask` — or we accept it's TA-only
   - **Leaning toward:** auto-check that `/ask` handler exists and calls
     both API + LLM; quality verified by TA

4. **Periodic health check verification:**
   - Hard to auto-check a background task
   - Could require a `--test-healthcheck` flag that runs one cycle and exits
   - **Leaning toward:** P1 (should have), TA-verified in demo

5. **Docker network:**
   - Bot needs to reach backend. If both in same compose, use service name.
   - If backend is separate compose, need shared network or host IP.
   - **Leaning toward:** require single compose file with both services
