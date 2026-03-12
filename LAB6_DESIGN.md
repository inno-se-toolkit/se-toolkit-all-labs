# Lab 06 — Build Your Own Agent: Design Document

> **Status:** Redesign v2. New task structure based on colleague feedback. Tasks and question bank need rewriting. Eval infrastructure (API endpoint, `run_eval.py`, `agent_eval` engine check) already implemented and reusable.

## 1. Lab Vision

**Slogan:** "Everybody should implement an agent loop at some point."

**One-liner:** Students build a CLI agent that reads their project wiki, answers questions about the course, then connects to their live system to analyze logs and diagnose bugs.

### 1.1 Why This Lab

Throughout the course, students used AI agents (labs 4-5) but never built one.
The risk: they copy-paste in early labs and vibe-code in later ones without
understanding what's happening under the hood. This lab forces understanding
at two levels:

1. **Agent mechanics** — they implement the loop (prompt → LLM → tool call →
   execute → feed result back → answer) and see there's no magic.
2. **Course material** — the evaluation questions cover all labs 1-6. To debug
   a wrong answer, the student must understand the material well enough to
   know what's correct. The agent is the vehicle; the questions are the test.

### 1.2 Design Principles

| Principle | Implication |
|-----------|-------------|
| **Deterministic first, open-ended later** | Task 1 has fully deterministic answers (wiki sections). Task 2 has mostly deterministic answers (static system facts). Task 3 adds open-ended chain questions. |
| **Learn by debugging, not by one-shotting** | Students iterate against a benchmark. They see what fails, diagnose why, fix it, re-run. |
| **Specify interfaces, not implementations** | We define CLI input/output format, tool schemas, eval criteria. How they build the agent is up to them. |
| **Evaluate the agent, evaluate the student** | The question bank tests both whether the agent works correctly AND whether the student understands the course material. |
| **Build on what exists** | The agent operates on their deployed lab 5 system. No new infrastructure. |
| **Progressive difficulty** | Wiki lookup → system queries → log analysis chains. Each task builds on the previous. |

### 1.3 Feedback Addressed

| Concern | Source | Resolution |
|---------|--------|------------|
| Tool use behavior depends on the model | Colleague 1 | LLM setup + tool calling verification moved to Setup. Recommend specific models known to work. |
| Weak models give inconsistent results ("pay-to-win") | Colleague 1 | Task 1 answers are deterministic (wiki sections). Model quality matters less when the answer is a fact. |
| Answers aren't deterministic or verifiable by students | Colleague 2 | Task 1: wiki section = deterministic. Task 2: static system facts = deterministic. Data queries use range checks. |
| Students will hardcode if error messages show expected answers | Colleague 2 | Hidden questions include chain-of-tool questions that can't be hardcoded. LLM judge for open-ended hidden questions. |
| Tool use questions come too late in benchmark | Colleague 1 | Task 1 requires tools from the start (read_file, list_files for wiki). No "no-tools" warm-up phase. |

---

## 2. Course Context — What Students Know

| Lab | Theme | Key Skills Acquired |
|-----|-------|---------------------|
| 1 | Product thinking, Git | Branching, PRs, issues, code review, architecture docs |
| 2 | Backend basics | FastAPI, Docker, Docker Compose, VM deployment |
| 3 | REST API + DB + Security | PostgreSQL, endpoints, auth, SSH hardening |
| 4 | Testing + Frontend + AI | pytest, React/TypeScript, using AI coding agents |
| 5 | Data pipeline + Analytics | ETL, httpx, SQL aggregation, Chart.js dashboards |
| 6 | **Build Your Own Agent** | **Agent loop, LLM API, tool calling, prompt engineering** |

---

## 3. Setup

Students begin with their lab 5 system deployed and running on their VM.
Setup now also includes LLM configuration and tool-calling verification.

### 3.1 Prerequisites (from lab 5)

- **Backend** (FastAPI) on port 42001 (via Docker)
- **Frontend** (React + Caddy) on port 42002
- **PostgreSQL** on port 42004
- **All services** running via `docker compose`
- **ETL pipeline** has been run (database has data)

### 3.2 LLM setup (new in v2)

Students create an OpenRouter account, get an API key, and configure
`.env.agent.secret`. They then run a provided verification script that tests:

1. **Basic LLM call** — send a prompt, get a response.
2. **Tool calling** — send a tool definition, verify the LLM returns a `tool_calls` response.

If tool calling fails, the student switches models before starting any graded work.

**Recommended models** (free, reliable tool calling):

| Model | Context | Tool calling | Notes |
|-------|---------|-------------|-------|
| `meta-llama/llama-4-scout:free` | 512k | Strong | Best free option |
| `meta-llama/llama-3.3-70b-instruct:free` | 128k | Strong | Reliable fallback |
| `qwen/qwen-2.5-72b-instruct:free` | 128k | Good | Alternative |

> **Key decision:** LLM setup is in Setup, not Task 1. Students discover
> model issues before any graded work. This directly addresses the
> "pay-to-win" and "tool use is weird" feedback.

---

## 4. Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│  Student's VM                                                │
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  agent.py    │────▶│  OpenRouter API (free LLM)       │   │
│  │  (CLI)       │◀────│  tool calling models              │   │
│  └──────┬───────┘     └──────────────────────────────────┘   │
│         │                                                    │
│         │ tool calls                                         │
│         ├──────────▶ read_file(path) ──▶ wiki/, source code  │
│         ├──────────▶ list_files(dir)  ──▶ wiki/, directories │
│         ├──────────▶ query_api(path)  ──▶ localhost:42002    │
│         │                                                    │
│  ┌──────┴───────┐                                            │
│  │  Docker      │  app (FastAPI) ─── postgres (data)         │
│  │  Compose     │  caddy (frontend)                          │
│  └──────────────┘                                            │
└──────────────────────────────────────────────────────────────┘
```

---

## 5. CLI Interface Specification

### 5.1 Input

```bash
python agent.py "How do you resolve a merge conflict?"
```

### 5.2 Output

```json
{
  "answer": "Edit the conflicting file, choose which changes to keep, then stage and commit.",
  "source": "wiki/git-workflow.md#resolving-merge-conflicts",
  "tool_calls": [
    {"tool": "list_files", "args": {"path": "wiki"}, "result": "git-workflow.md\n..."},
    {"tool": "read_file", "args": {"path": "wiki/git-workflow.md"}, "result": "..."}
  ]
}
```

**Fields:**
- `answer` (string, required) — the agent's answer to the question.
- `source` (string, optional) — wiki section reference for wiki questions (`wiki/file.md#section`). Required in Task 1, optional in Tasks 2-3.
- `tool_calls` (array, required) — list of tool calls made. Empty array if none.

**Rules:**
- Output MUST be valid JSON on a single line to stdout.
- Debug/progress output goes to stderr only.
- 60-second timeout per question.
- Exit code 0 on success.
- Maximum 10 tool calls per question.

---

## 6. Required Tools

### 6.1 `read_file`

```
Name:        read_file
Parameters:  path (string, required) — relative path from project root
Returns:     File contents as string, or error message if not found
Security:    Must restrict to project directory
```

Used in Task 1 (wiki files) and Task 2 (source code, logs).

### 6.2 `list_files`

```
Name:        list_files
Parameters:  path (string, required) — relative directory path
Returns:     Newline-separated listing of entries
Security:    Must restrict to project directory
```

Used in Task 1 (discover wiki files) and Task 2 (explore code structure).

### 6.3 `query_api`

```
Name:        query_api
Parameters:  method (string) — HTTP method (GET, POST)
             path (string) — API path, e.g. "/items/"
             body (string, optional) — JSON request body
Returns:     JSON with status_code and body
Auth:        Uses LMS_API_KEY from .env.docker.secret
```

Introduced in Task 2 for system queries.

---

## 7. Question Classes and Benchmark Design

### 7.1 Output format (all classes)

```json
{
  "answer": "The text answer",
  "source": "wiki/file.md#section",
  "tool_calls": [{"tool": "...", "args": {...}, "result": "..."}]
}
```

### 7.2 Class A: Wiki lookup (Task 1)

**What:** Questions about course material. The answer lives in a wiki section.

**Example:**
```
Q: "How do you resolve a merge conflict?"
→ answer: "Edit the conflicting file, choose which changes to keep, then stage and commit."
→ source: "wiki/git-workflow.md#resolving-merge-conflicts"
→ tool_calls: [list_files("wiki"), read_file("wiki/git-workflow.md")]
```

**Checking:**

| Check | Method | Required |
|-------|--------|----------|
| Source section | `source` field matches expected path (exact or `any_of`) | Yes |
| Answer relevance | `answer` contains keywords from the section | Optional |
| Tool usage | `tool_calls` includes `read_file` or `list_files` | Yes |

**Why deterministic:** The correct section is a fact. Either the agent found it or it didn't. Students can verify by reading the section themselves.

**Prerequisite:** The wiki must comprehensively cover labs 1-6 material.

**Count:** ~15 in `run_eval.py`, ~5 hidden in bot eval.

### 7.3 Class B: Static system facts (Task 2)

**What:** Questions about the system where the answer is always the same regardless of data. Config values, ports, frameworks, status codes.

**Example:**
```
Q: "What HTTP status code does the API return when you request /items/ without authentication?"
→ answer: "401 Unauthorized"
→ tool_calls: [{tool: "query_api", args: {method: "GET", path: "/items/"}}]
```

**Checking:**

| Check | Method | Required |
|-------|--------|----------|
| Answer | `contains`, `any_of`, or `regex` | Yes |
| Tool usage | `tool_calls` includes expected tool | Yes |

**Why deterministic:** These values are baked into the code/config. Port 8000 is always 8000. Unauthenticated request always returns 401.

**Examples:**
- "What framework does the backend use?" → contains "FastAPI", expects `read_file`
- "What port does FastAPI listen on inside the container?" → contains "8000", expects `read_file`
- "What status code for a nonexistent endpoint?" → contains "404", expects `query_api`
- "What ORM does the project use?" → contains "SQLModel", expects `read_file`

**Count:** ~8 in `run_eval.py`, ~3 hidden.

### 7.4 Class C: Data-dependent system queries (Task 2)

**What:** Questions about live data. Answer varies per student but can be range-checked.

**Example:**
```
Q: "How many items are currently in the database?"
→ answer: "There are 47 items."
→ tool_calls: [{tool: "query_api", args: {method: "GET", path: "/items/"}}]
```

**Checking:**

| Check | Method | Required |
|-------|--------|----------|
| Answer plausibility | `numeric_gt` or `numeric_range` | Yes |
| Tool usage | `tool_calls` includes `query_api` | Yes |

**Why it works:** We don't check exact numbers. We check that a number exists and is in a plausible range. The tool call proves the agent actually queried the system.

**Count:** ~3 in `run_eval.py`, ~2 hidden.

### 7.5 Class D: Log analysis chain (Task 3, hidden only)

**What:** Multi-step questions requiring a chain of tool calls. Planted bugs produce log errors that the agent must find, trace to source, and diagnose.

**Example:**
```
Q: "Check the application logs for errors. What is causing the most recent error and which file is it in?"
→ answer: "ZeroDivisionError in backend/app/routers/analytics.py line 42,
   in average_score when group has no submissions. Fix: check for empty results."
→ tool_calls: [
    {tool: "query_api", args: {path: "/logs"}},
    {tool: "read_file", args: {path: "backend/app/routers/analytics.py"}}
  ]
```

**Checking:**

| Check | Method | Required |
|-------|--------|----------|
| Bug identified | `answer` contains bug identifier (e.g., "ZeroDivisionError") | Yes |
| Source file found | `answer` contains expected file path | Yes |
| Fix suggested | `answer` contains fix keyword (e.g., "check", "empty") | Optional |
| Tool chain | `tool_calls` includes log-reading AND file-reading tools | Yes |
| Fix quality | LLM judge with rubric | Optional |

**Planted bugs:**

| Bug | Where | Log output | Expected identification |
|-----|-------|-----------|----------------------|
| Division by zero on empty group | `analytics.py` | `ZeroDivisionError` in logs | Error + file + empty-check fix |
| Unclosed resource in edge case | `etl.py` | `ResourceWarning` in logs | Warning + file + context-manager fix |
| Hardcoded timeout as string | `config.py` | `TypeError` caught and logged | Type error + file + int conversion fix |

**Why this works:** Bugs are planted by us. We know exactly what the logs contain and what the correct diagnosis is. Checking is keyword-based (bug name, file path) plus optional LLM judge.

**Count:** 3-5 hidden questions (bot eval only).

### 7.6 Class E: LLM-judged reasoning (Task 3, hidden only)

**What:** Open-ended questions where keyword matching isn't sufficient. An LLM judge evaluates the answer against a rubric.

**Example:**
```
Q: "Compare how the ETL pipeline handles failures vs how the API endpoints
    handle failures. Which approach is more robust and why?"
→ answer: "The ETL pipeline uses idempotent upserts so partial failures
   can be retried... The API endpoints return error codes but don't have
   retry logic... ETL is more robust because..."
→ tool_calls: [read_file("backend/app/etl.py"), read_file("backend/app/routers/...")]
```

**Checking:**

| Check | Method | Required |
|-------|--------|----------|
| Answer quality | LLM judge (rubric: mentions both, compares, gives reasoning) | Yes |
| Tool usage | `tool_calls` includes `read_file` for relevant files | Yes |

**Budget:** ~5 questions × ~$0.01 per judge call = ~$0.05/student. For 60 students = ~$3 total. Use a cheap fast model (Haiku/Flash) as judge.

**Count:** 3-5 hidden questions (bot eval only).

### 7.7 Summary: questions per task

| Class | Task | `run_eval.py` | Bot-only | Checking method |
|-------|------|--------------|----------|-----------------|
| A: Wiki lookup | 1 | ~15 | ~5 | Section path match + tool use |
| B: Static system facts | 2 | ~8 | ~3 | Keyword match + tool use |
| C: Data-dependent queries | 2 | ~3 | ~2 | Numeric range + tool use |
| D: Log analysis chain | 3 | 0 | 3-5 | Bug ID + file + tool chain |
| E: LLM-judged reasoning | 3 | 0 | 3-5 | LLM judge with rubric |
| **Total** | | **~26** | **~13-17** | |

---

## 8. Task Structure (v2)

### Setup — LLM and System Verification

**Goal:** Verify lab 5 system is running, set up LLM with tool calling.

**What's new vs v1:** LLM setup + tool calling verification moves here.
Students discover model issues before any graded work.

**Deliverables:**
1. Fork and clone repo
2. Verify lab 5 system on VM (SSH, API reachable, data exists)
3. Create OpenRouter account, configure `.env.agent.secret`
4. Run verification script: basic LLM call + tool calling test pass

### Task 1 — The Documentation Agent

**Goal:** Build an agent that answers questions by finding the relevant wiki section and providing the answer.

**Narrative:** "Your project has a wiki full of documentation. Build an agent that reads it for you — given a question, it finds the right section and answers from it."

**What students build:**
- `agent.py` CLI with JSON output (answer + source + tool_calls)
- Tools: `read_file`, `list_files` (to navigate `wiki/`)
- Agentic loop: list wiki files → read relevant file → identify section → answer
- System prompt that understands the task

**What students learn:**
- LLM API integration with tool calling
- The agentic loop (call LLM → execute tool → feed back → repeat)
- CLI design with structured JSON output
- How agents use tools to ground answers in real data (not hallucinate)

**Benchmark:** ~15 Class A (wiki lookup) questions. All deterministic.

### Task 2 — The System Agent

**Goal:** Connect the agent to the live system so it can answer questions about the actual deployment.

**Narrative:** "Your agent can read docs. Now give it access to the running system — the API, the codebase, the configuration. Make it useful."

**What students build:**
- `query_api` tool (HTTP requests to the backend)
- Extended `read_file` use (source code, config, docker-compose.yml)
- Updated system prompt for system questions

**What students learn:**
- HTTP API integration from code
- Authentication (API key handling)
- Querying live systems vs reading static files
- Debugging real system behavior

**Benchmark:** ~15 wiki (Class A) + ~11 system (Class B + C) questions.

### Task 3 — Pass the Benchmark

**Goal:** Pass the full benchmark including hidden chain-of-tool and reasoning questions.

**Narrative:** "Your agent works for docs and basic system queries. Now it faces harder questions — diagnosing bugs from logs, chaining multiple tools, and reasoning about the system."

**What students build:**
- Improved prompts for multi-step reasoning
- Handling of log data (errors, tracebacks)
- Robust tool error handling
- Edge case fixes from benchmark iteration

**What students learn:**
- Prompt engineering through iteration
- Multi-step agent reasoning (logs → source → diagnosis)
- That agent quality comes from iteration, not writing code once
- Debugging agent behavior systematically

**Benchmark:** All local questions + hidden questions (Class D: log chains, Class E: LLM-judged).

**Planted bugs:** 2-3 non-critical bugs in the backend that produce log entries. The agent must find, trace, and diagnose them.

---

## 9. Evaluation System

### 9.1 Two evaluation paths

| | Local eval (`run_eval.py`) | Bot eval (autochecker SSH) |
|--|---------------------------|---------------------------|
| **Triggered by** | Student runs locally | Student sends `/check` in Telegram |
| **Questions** | ~26 (from API) | ~26 + ~13-17 hidden |
| **Where agent runs** | Student's machine | Student's VM (via SSH) |
| **Matching logic** | In `run_eval.py` (shipped with repo) | In autochecker engine |
| **Display** | Green pass, stop at first fail | Same |
| **Purpose** | Fast iteration | Grading |

### 9.2 Matching strategies

| Strategy | Rule | Used by |
|----------|------|---------|
| `source_match` | `source` field matches expected section path | Class A |
| `contains` | Answer contains substring (case-insensitive) | Class B |
| `contains_all` | Answer contains all substrings | Class B |
| `any_of` | Answer contains any substring | Class B |
| `regex` | Answer matches pattern | Class B |
| `numeric_gt` | Answer contains number > N | Class C |
| `numeric_range` | Answer contains number in [min, max] | Class C |
| `tool_chain` | `tool_calls` includes expected sequence of tool names | Class D |
| `llm_judge` | LLM evaluates answer against rubric | Class E |

### 9.3 Anti-gaming

- Task 1 answers are deterministic — hardcoding is visible (student must have wiki files).
- Hidden questions include multi-tool chains that can't be hardcoded.
- LLM judge for open-ended hidden questions makes hardcoding impractical.
- Tool call verification ensures the agent actually used tools (not just returned a string).
- Every API request is logged (student email, timestamp, question index).

### 9.4 `run_eval.py`

Ships with the repo. Fetches questions from autochecker API, runs agent locally, evaluates. Stop-at-first-failure.

```bash
python run_eval.py           # run all questions sequentially
python run_eval.py --index 5 # test a single question (for debugging)
```

---

## 10. Wiki Requirements

Task 1 depends on a comprehensive wiki. The wiki must cover:

| Topic | Lab | Suggested wiki file |
|-------|-----|-------------------|
| Git workflow | 1 | `wiki/git-workflow.md` |
| Branching, PRs, reviews | 1 | `wiki/git-workflow.md` |
| Backend basics, FastAPI | 2 | `wiki/backend.md` |
| Docker, Compose, volumes | 2 | `wiki/docker.md` |
| REST API, HTTP methods | 3 | `wiki/rest-api.md` |
| Database, SQL, ORM | 3 | `wiki/database.md` |
| Authentication, security | 3 | `wiki/security.md` |
| Testing, pytest | 4 | `wiki/testing.md` |
| Frontend, React | 4 | `wiki/frontend.md` |
| ETL, data pipelines | 5 | `wiki/etl.md` |
| Analytics, SQL aggregation | 5 | `wiki/analytics.md` |
| Agents, tool calling | 6 | `wiki/agents.md` |

**Action needed:** Audit existing wiki content, identify gaps, write missing sections.

---

## 11. Planted Bugs (Task 3)

Non-critical bugs in the backend that produce log entries but don't break functionality.

| # | Bug | File | Log output | Trigger |
|---|-----|------|-----------|---------|
| 1 | Division by zero when a group has no submissions | `analytics.py` | `ZeroDivisionError` caught, logged | GET `/analytics/scores?group=empty-group` |
| 2 | Unclosed resource warning in ETL edge case | `etl.py` | `ResourceWarning` logged | POST `/pipeline/sync` with empty response |
| 3 | Config type mismatch (string timeout) | `config.py` | `TypeError` caught, logged | Any request after startup |

These bugs must:
- Not break existing lab 5 functionality or autochecker checks.
- Produce visible log entries that the agent can find.
- Be diagnosable by reading the source code.
- Have clear fixes that the agent can suggest.

---

## 12. Decisions Made

| # | Question | Decision |
|---|----------|----------|
| 1 | Starter `agent.py` skeleton? | **No** — students build from scratch, plan first |
| 2 | LLM setup when? | **Setup task** — verify tool calling before graded work |
| 3 | Model recommendation? | **Strong models first** — Llama 4 Scout, Llama 3.3 70B, Qwen 2.5 72B |
| 4 | Task 1 approach? | **Wiki lookup** — deterministic, verifiable, teaches tools from day one |
| 5 | Task 1 output? | **Answer + source** — source is deterministic, answer shows understanding |
| 6 | Tool call verification? | Loose — check tool was used, not exact args |
| 7 | Max agent loop iterations? | **10** tool calls per question |
| 8 | How to handle non-deterministic system questions? | Static facts (deterministic) + range checks for data-dependent |
| 9 | How to prevent hardcoding? | Hidden chain-of-tool questions + LLM judge for reasoning |
| 10 | Input format? | **Plain string argument** (`python agent.py "..."`) |
| 11 | API key naming? | **`LMS_API_KEY`** (backend) vs **`LLM_API_KEY`** (LLM provider) |
| 12 | LLM config file? | **`.env.agent.secret`** (gitignored), with `.env.agent.example` committed |
| 13 | Planted bugs for Task 3? | **Yes** — 2-3 non-critical bugs producing log entries |
| 14 | LLM judge for hidden questions? | **Yes** — budget ~$3 total for 60 students |
| 15 | `run_eval.py` features? | Add `--index N` flag for single-question debugging |

---

## 13. Remaining Work

- [ ] Audit existing wiki content — what's there, what's missing
- [ ] Write missing wiki sections (labs 1-6 material)
- [ ] Rewrite Task 1 (`task-1.md`) — documentation agent
- [ ] Rewrite Task 2 (`task-2.md`) — system agent
- [ ] Rewrite Task 3 (`task-3.md`) — pass the benchmark (with planted bugs)
- [ ] Update setup task — add LLM setup and verification script
- [ ] Create verification script (`verify_llm.py`)
- [ ] Write Class A questions (wiki lookup, ~20)
- [ ] Write Class B questions (static system facts, ~11)
- [ ] Write Class C questions (data-dependent queries, ~5)
- [ ] Write Class D questions (log analysis chains, ~5)
- [ ] Write Class E questions (LLM-judged reasoning, ~5)
- [ ] Implement planted bugs in backend
- [ ] Add `source_match` check to `run_eval.py` and engine
- [ ] Add `tool_chain` check to engine
- [ ] Add `llm_judge` check to engine (with budget control)
- [ ] Update autochecker spec (`lab-06.yaml`)
- [ ] Update `run_eval.py` with `--index` flag
- [ ] Update README and lab-plan to match v2 design
- [ ] Update optional task
