# Lab 06 — Build Your Own Agent: Design Document

> **Status:** All 3 tasks written. Question bank (v2) created. Eval API endpoint deployed. `run_eval.py` shipped. Autochecker spec pending.

## 1. Lab Vision

**Slogan:** "Everybody should implement an agent loop at some point."

**One-liner:** Students build a CLI agent from scratch that answers questions
about their system and the course, evaluated against a hidden benchmark —
like building an algorithm against a test suite.

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
| **Learn by debugging, not by one-shotting** | Students iterate against a benchmark. They see what fails, diagnose why, fix it, re-run. The debugging loop IS the learning. |
| **Specify interfaces, not implementations** | We define CLI input/output format, tool schemas, eval criteria. How they build the agent is up to them. They can plan with an AI agent. |
| **Evaluate the agent, evaluate the student** | The question bank tests both whether the agent works correctly AND whether the student understands the course material. |
| **Build on what exists** | The agent operates on their deployed lab 5 system. No new infrastructure — they already have a VM, a backend, a database, a frontend. |
| **Clearly useful** | The agent helps them understand their own system and review course material. It's not a toy exercise. |
| **Progressive difficulty** | Basic questions work with just an LLM. Tool questions require real tool implementations. Edge cases require iteration and prompt engineering. |

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

**Desired vs actual gap:** Labs 1-3 are heavily scaffolded (follow steps, fix
prescribed bugs, copy patterns). Lab 4 introduces AI agents as a tool to use,
not to understand. Lab 5 is more independent but still template-driven. Many
students completed the work without deeply understanding what they built.

**Lab 6 closes this gap** by requiring students to:
- Build an agent that demonstrates understanding of the mechanics
- Answer questions that require understanding of the course material
- Debug failures that require understanding of their own system

---

## 3. Prerequisites and Setup

Students begin with their lab 5 system deployed and running on their VM:

- **Backend** (FastAPI) on port 42001 (via Docker)
- **Frontend** (React + Caddy) on port 42002
- **PostgreSQL** on port 42004
- **All services** running via `docker compose`
- **ETL pipeline** has been run (database has data)
- **Analytics endpoints** are implemented and functional

**Setup task:** Verify that their lab 5 deployment is operational. The
autochecker will validate SSH access, API reachability, and that the database
contains data before running agent evaluations.

---

## 4. Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│  Student's VM                                                │
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  agent.py    │────▶│  OpenRouter API (free LLM)       │   │
│  │  (CLI)       │◀────│  meta-llama/llama-3.3-70b:free   │   │
│  └──────┬───────┘     └──────────────────────────────────┘   │
│         │                                                    │
│         │ tool calls                                         │
│         ├──────────▶ read_file(path) ──▶ local filesystem    │
│         ├──────────▶ list_files(dir)  ──▶ local filesystem   │
│         ├──────────▶ query_api(path)  ──▶ localhost:42002    │
│         │                                                    │
│  ┌──────┴───────┐                                            │
│  │  Docker      │  app (FastAPI) ─── postgres (data)         │
│  │  Compose     │  caddy (frontend)                          │
│  └──────────────┘                                            │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  Autochecker                                                 │
│                                                              │
│  SSH ──▶ python agent.py "..." ──▶ stdout     │
│       ◀── JSON output (answer + tool_calls)                  │
│                                                              │
│  Compare answer against expected ──▶ PASS / FAIL             │
└──────────────────────────────────────────────────────────────┘
```

---

## 5. LLM Access

### Decision: OpenRouter with free models

**Chosen:** OpenRouter free tier.

**Rationale:**
- Zero cost — no credit card, no budget concerns
- OpenAI-compatible API (`POST /v1/chat/completions`) — transferable knowledge
- 18 free models support tool/function calling
- Students create an account, get an API key, done

**Alternatives considered:**

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| OpenRouter free | Zero cost, many models, tool support | Rate limits (RPM/RPD), model quality varies | **Selected** |
| Shared API key | Equal access, no student setup | Key leaks, hard to rate-limit per student | Rejected |
| Students bring own | Flexibility | Unequal access, cost barrier, harder to debug | Rejected |
| Local models (Ollama) | No API dependency | VM resources limited, tool calling unreliable | Rejected |

**Recommended default model:** `meta-llama/llama-3.3-70b-instruct:free`
- 128k context, strong tool calling, good instruction following
- Students may switch to any free model with tool support

**Configuration:** Students store LLM credentials in `.env.agent.secret`
(gitignored by the `*.secret` pattern). An `.env.agent.example` is committed:
- `LLM_API_KEY` — LLM provider API key
- `LLM_API_BASE` — OpenAI-compatible endpoint URL
- `LLM_MODEL` — model name

> **Two distinct keys:** `LMS_API_KEY` (in `.env.docker.secret`) protects
> the backend LMS endpoints. `LLM_API_KEY` (in `.env.agent.secret`)
> authenticates with the LLM provider. The rename from `API_KEY` to
> `LMS_API_KEY` was done to avoid this confusion.

**Rate limits (free tier):**
- Requests per minute: capped (exact value varies)
- Requests per day: capped; increases if user has purchased credits
- Sufficient for lab work — students aren't doing bulk inference
- If rate-limited: wait and retry (good practice to implement)

---

## 6. Tool Interface

### Decision: OpenAI-style function calling

**Chosen:** Standard OpenAI function calling format via the `tools` parameter
in the chat completions API.

**Rationale:** This IS how agents work in practice. The pedagogical goal is to
demystify agents — using the real industry standard serves that directly.
OpenRouter's free models support it natively.

**Alternatives considered:**

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| OpenAI-style `tools` param | Industry standard, LLM handles parsing, structured | More boilerplate | **Selected** |
| Provided SDK/wrapper | Less boilerplate | Hides how agents work — defeats the goal | Rejected |
| Free-form text parsing | Simple concept | Fragile, wastes time on regex bugs, non-standard | Rejected |

### How it works

Students define tools as JSON schemas in their API request:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a file from the project repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root, e.g. 'backend/app/main.py'"
                    }
                },
                "required": ["path"]
            }
        }
    }
]
```

The LLM returns structured tool calls:

```json
{
  "tool_calls": [
    {
      "id": "call_123",
      "function": {
        "name": "read_file",
        "arguments": "{\"path\": \"backend/app/main.py\"}"
      }
    }
  ]
}
```

The student executes the tool, sends the result back as a `tool` message,
and the LLM incorporates it into its final answer.

---

## 7. Required Tools

Students must implement these tools for their agent. The tool names and
parameter schemas are prescribed (the autochecker verifies tool usage in
the output). The implementation is up to the student.

### 7.1 `read_file`

Read the contents of a file from the project repository.

```
Name:        read_file
Parameters:  path (string, required) — relative path from project root
Returns:     File contents as string, or error message if file not found
Example:     read_file("backend/app/main.py") → "from fastapi import FastAPI..."
```

**What it enables:** Code inspection questions — "What framework does the
backend use?", "What ORM is used?", "How does authentication work?"

Security: must restrict to the project directory (no reading `/etc/passwd`).

### 7.2 `list_files`

List files and directories at a given path.

```
Name:        list_files
Parameters:  path (string, required) — relative directory path from project root
Returns:     List of filenames/subdirectories as string
Example:     list_files("backend/app/routers") → "analytics.py\ninteractions.py\nitems.py\n..."
```

**What it enables:** Discovery questions — "How many routers does the backend
have?", "What source files are in the frontend?"

### 7.3 `query_api`

Make an HTTP request to the deployed backend API.

```
Name:        query_api
Parameters:  method (string, required) — HTTP method (GET, POST)
             path (string, required) — API path, e.g. "/analytics/scores?lab=lab-04"
             body (string, optional) — JSON request body for POST requests
Returns:     JSON string with status_code and response body
Example:     query_api("GET", "/items/") → {"status": 200, "body": [{"id": 1, ...}]}
```

**What it enables:** System introspection — "How many items are in the
database?", "What is the average score for lab-04?", "What status code does
an unauthenticated request return?"

The tool must handle authentication (include `LMS_API_KEY` from
`.env.docker.secret` in the request header as a Bearer token).

---

## 8. CLI Interface Specification

### 8.1 Input

The agent is invoked via command line with a plain string argument:

```bash
python agent.py "What does REST stand for?"
```

The question is the first positional argument. No JSON wrapping.

### 8.2 Output

The agent prints a single JSON object to stdout:

```json
{
  "answer": "REST stands for Representational State Transfer.",
  "tool_calls": [
    {
      "tool": "read_file",
      "args": {"path": "backend/app/main.py"},
      "result": "from fastapi import FastAPI..."
    }
  ]
}
```

Output schema:
```json
{
  "answer": "string (required) — the agent's final answer",
  "tool_calls": [
    {
      "tool": "string — tool name",
      "args": "object — arguments passed to the tool",
      "result": "string — tool execution result (truncated to 500 chars)"
    }
  ]
}
```

**Rules:**
- Output MUST be valid JSON on a single line to stdout
- `answer` is required and must directly answer the question
- `tool_calls` is required (empty array `[]` if no tools were used)
- Any logs, debug output, or progress messages go to stderr, not stdout
- The agent must complete within 60 seconds per question
- Exit code 0 on success, non-zero on error

### 8.3 Consistent across all tasks

The interface is the same from task 1 through task 3. In task 1, `tool_calls`
will be `[]` because no tools are implemented yet. By task 2, tool calls
should appear for questions that require them.

---

## 9. Evaluation Design

> **Note:** This section provides the conceptual overview. Section 13 has
> the full implementation details (API endpoint, matching strategies, bot eval).

### 9.1 How evaluation works

Two paths: local iteration (`run_eval.py`) and grading (autochecker SSH).

**Local iteration:** Students run `python run_eval.py` which fetches questions
one at a time from the autochecker API, runs their agent locally, and checks
the answer. Stops at the first failure — students fix that question and re-run.

**Grading:** The autochecker bot SSHes into the student's VM, runs the agent
with 34 questions (25 shared + 9 bot-only), same stop-at-first-failure display.

### 9.2 What students see

Stop-at-first-failure — green for each pass, red for the first fail, then stop:

```
  + [1/25] A teammate pushes broken code directly to main...
  + [2/25] You see a commit message that just says 'fix'...
  + [3/25] Your teammate and you both edited the same line...

  x [4/25] You change your Python code and run 'docker compose up -d'...
    Your answer: restart the container
    Expected: answer should contain any of: ["--build", "build", ...]

3/25 passed
```

**Key design choices:**
- Show expected answer on failure so students can fix their agent.
- Stop at first failure to force sequential debugging (one fix at a time).
- Questions ordered by difficulty: knowledge-only first, then tool-required.
- Question bank is NOT revealed upfront — students discover questions by running eval.

### 9.3 Answer matching strategies

See section 13.2 for the full matching strategy table. Strategies include:
`contains`, `contains_all`, `any_of`, `regex`, `numeric_gt`, `numeric_range`.

### 9.4 Anti-gaming

- The 9 bot-only questions are never served by the API — only encountered via autochecker SSH.
- Students must build a genuinely working agent, not hard-code answers.
- Every API request is logged (student email, timestamp, question index).

---

## 10. Question Bank Design

**File:** `lab-06-eval.yaml` (in parent repo, not shipped to students)

### 10.1 Structure

**File:** `autochecker/specs/lab-06-eval.yaml` (v2)

- **25 script questions** (index 0-24) — served by the API for local testing
- **9 bot-only questions** (index 25-33) — only in autochecker SSH eval
- **34 total** for grading

Questions are derived from learning outcomes of labs 1-6. Scenario/understanding-
focused — no trivia or "define X" filler. Ordered by difficulty within each tier.

### 10.2 Topic coverage

Questions map to labs 1-6 learning outcomes:

| Topic | Labs | Examples |
|-------|------|----------|
| Git workflow | 1 | Branch protection, merge conflicts, conventional commits |
| HTTP & REST | 2-3 | Status codes, methods, idempotency, auth |
| Docker | 2 | Build vs recreate, volumes, compose commands |
| SQL & Databases | 3 | Migrations, ORM, constraints |
| Testing | 4 | Pytest, test isolation, code coverage |
| ETL & Analytics | 5 | Extract-Transform-Load, data pipelines |
| Agents | 6 | Agent loop, tool calling, prompt engineering |
| System-specific | 2-5 | Requires `read_file`, `list_files`, or `query_api` tools |

### 10.3 Tier breakdown

| Tier | After task | Description | Script | Bot-only | Total |
|------|-----------|-------------|--------|----------|-------|
| 1 | Task 1 | Course knowledge, no tools needed | 17 | 0 | 17 |
| 2 | Task 2 | Requires tool implementations | 8 | 5 | 13 |
| 3 | Task 3 | Tools + reasoning, edge cases | 0 | 4 | 4 |

### 10.4 Black-box design

- Students never see the question bank file.
- The API serves one question at a time by index.
- The 9 bot-only questions prevent gaming — students must build a real agent.
- Stop-at-first-failure forces sequential debugging.

---

## 11. Task Structure

> Tasks are deliverable-focused (WHAT, not HOW). Each follows:
> git workflow → what you build → CLI interface → deliverables → acceptance criteria.
>
> Git workflow per task: Issue → branch (e.g. `task/basic-agent-loop`) →
> conventional commits → PR to fork's `main` with `Closes #N` → review → merge → close → delete branch.

### Task 1: Basic Agent Loop — WRITTEN

**Goal:** Build a CLI that takes a question, calls an LLM, and returns an answer.

**File:** `lab/tasks/required/task-1.md`

**Deliverables** (5, each with a prescribed commit message):
1. **Plan** (`plans/task-1.md`) — provider choice, structure, system prompt strategy
2. **Agent** (`agent.py`) — CLI in project root, plain string input, JSON output
3. **Documentation** (`AGENT.md`) — architecture, provider, system prompt, how to run
4. **Tests** (5 regression tests) — subprocess, parse JSON, check keywords
5. **Deployment** — agent works on VM via SSH

**Interface:**
```bash
python agent.py "What does REST stand for?"
# stdout: {"answer": "Representational State Transfer.", "tool_calls": []}
```

**Acceptance criteria include:** issue closed by PR, plan committed before code,
5 tests pass, agent works on VM.

### Task 2: Add Tools — WRITTEN

**Goal:** Implement tools (read_file, list_files, query_api) and the agentic loop.

**File:** `lab/tasks/required/task-2.md`

**Deliverables** (5, each with a prescribed commit message):
1. **Plan** (`plans/task-2.md`) — tool schemas, loop design, security
2. **Tools + loop** (update `agent.py`) — 3 tools, agentic loop, tool_calls populated
3. **Documentation** (update `AGENT.md`) — tools, loop, new config
4. **Tests** (5 regression tests) — verify tool_calls non-empty, correct tool names
5. **Deployment** — tools work on VM, `LMS_API_KEY` available for `query_api`

**Tools:** `read_file(path)`, `list_files(path)`, `query_api(method, path, body?)`.
Security: restrict file tools to project dir. Auth: `query_api` uses `LMS_API_KEY`.
Agentic loop: max 10 tool calls per question.

### Task 3: Pass the Benchmark — WRITTEN

**Goal:** Iterate on the agent until it passes the full eval benchmark (≥75%).

**File:** `lab/tasks/required/task-3.md`

**Deliverables** (5, each with a prescribed commit message):
1. **Plan** (`plans/task-3.md`) — initial score, first failures, strategy
2. **Agent improvements** (update `agent.py`) — iterate until 25/25 locally
3. **Documentation** (update `AGENT.md`) — final architecture, lessons learned, eval score
4. **Tests** — updated regression tests with benchmark edge cases
5. **Deployment** — agent passes autochecker bot (≥26/34 = 75%)

**Key features:**
- Debugging workflow table (symptom → likely cause → fix)
- `run_eval.py` as the primary iteration tool
- Stop-at-first-failure forces sequential diagnosis

**What students learn:**
- Prompt engineering through iteration (not theory)
- Debugging agent behavior (examining tool calls, prompt issues)
- Course material — by examining correct and incorrect answers
- That agent quality comes from iteration, not from writing code once

---

## 12. Student Workflow

### 12.1 Development cycle

```
1. Write/modify agent code
         │
         ▼
2. Test locally
   python agent.py "..."
         │
         ▼
3. Examine output — is the answer correct?
   ├── Yes → try another question
   └── No → debug:
       ├── LLM gave wrong answer → fix system prompt
       ├── Tool wasn't called → fix tool description
       ├── Tool returned error → fix tool implementation
       └── Tool called but wrong args → improve prompt/schema
         │
         ▼
4. Push code, run autochecker (via Telegram bot or manually)
         │
         ▼
5. See eval results:
   ✅ green = passed (examine to learn)
   ❌ red = failed (target for next fix)
         │
         ▼
6. Pick one failed question → go to step 1
```

### 12.2 What happens where

| Action | Where | Who/What does it |
|--------|-------|-----------------|
| Edit agent code | Student's laptop / VM | Student (can use AI assistant to plan) |
| Test agent locally | Student's VM | Student runs `python agent.py "..."` |
| Deploy/commit code | Student's VM / GitHub | Student pushes to repo |
| Run eval | Student's VM (via SSH) | Autochecker SSHes in, runs agent |
| View results | Telegram bot / dashboard | Student reads pass/fail output |
| Fix issues | Student's laptop / VM | Student iterates |

### 12.3 What the student does manually vs what the agent does

| Activity | Done by |
|----------|---------|
| Writing the agent code | Student (may use AI coding assistant) |
| Choosing tools to implement | Student |
| Writing the system prompt | Student |
| Defining tool schemas | Student |
| Running the agent | Autochecker (via SSH) |
| Calling the LLM | The agent (student's code) |
| Selecting which tool to call | The LLM (via function calling) |
| Executing the tool | The agent (student's code) |
| Interpreting tool results | The LLM |
| Producing the final answer | The LLM |
| Evaluating the answer | Autochecker |
| Debugging failures | Student |
| Improving prompts | Student |

### 12.4 `run_eval.py` — the primary iteration tool

Students iterate using the shipped `run_eval.py` script:

```bash
python run_eval.py
```

The script reads autochecker credentials from `.env` / `.env.docker.secret`,
fetches 25 questions one at a time from the API, runs the agent locally,
and evaluates answers. Stops at the first failure with diagnostic output.

This replaces manual question-by-question testing. Students also write
regression tests (unit tests for tools, subprocess tests for the full agent)
to catch regressions as they iterate.

---

## 13. Evaluation System

### 13.1 Two evaluation paths

| | Local eval (`run_eval.py`) | Bot eval (autochecker SSH) |
|--|---------------------------|---------------------------|
| **Triggered by** | Student runs locally | Student sends `/check` in Telegram |
| **Questions** | 25 (from API) | 34 (25 shared + 9 bot-only) |
| **Where agent runs** | Student's machine | Student's VM (via SSH) |
| **Matching logic** | In `run_eval.py` (shipped with repo) | In autochecker |
| **Display** | Passes shown green, stop at first fail | Same |
| **Purpose** | Fast iteration | Grading |

### 13.2 Local eval API endpoint

Students iterate locally using `run_eval.py`, which fetches questions
from the autochecker API one at a time.

**Auth:** Same credentials as lab 5 (`AUTOCHECKER_EMAIL` / `AUTOCHECKER_PASSWORD`).
Students already have these configured in `.env`.

```
GET /api/eval/question
  Auth: Basic <base64(email:password)>
  Query: ?lab=lab-06&index=0
  →
  {
    "index": 0,
    "total": 25,
    "question": "What does REST stand for?",
    "expected": {"contains": "Representational State Transfer"}
  }
```

- Returns question + expected answer for the given index.
- `expected` contains the matching rule — the script evaluates locally.
- Returns `404` if index >= total.
- Server logs every request: student email, timestamp, question index.

**Matching strategies** (implemented in `run_eval.py`):

| Strategy | Rule | Example |
|----------|------|---------|
| `contains` | Answer contains substring (case-insensitive) | `{"contains": "FastAPI"}` |
| `contains_all` | Answer contains all substrings | `{"contains_all": ["Extract", "Transform", "Load"]}` |
| `any_of` | Answer contains any substring | `{"any_of": ["PUT", "put"]}` |
| `regex` | Answer matches pattern | `{"regex": "\\b40[14]\\b"}` |
| `numeric_gt` | Answer contains number > N | `{"numeric_gt": 0}` |
| `numeric_range` | Answer contains number in [min, max] | `{"numeric_range": [0, 100]}` |

**`run_eval.py` loop** (ships with the repo, ~50 lines):

```
login with AUTOCHECKER_EMAIL / AUTOCHECKER_PASSWORD → token
index = 0

loop:
  resp = GET /api/eval/question?lab=lab-06&index={index}
  if 404 → print "25/25 PASSED", exit

  output = subprocess: python agent.py "{resp.question}"
  parse JSON from stdout

  if matches(output.answer, resp.expected):
    print green: ✅ {resp.question}
    index += 1
  else:
    print red:  ❌ {resp.question}
                   Your answer: {output.answer}
                   Expected: {resp.expected}
    exit
```

### 13.3 Bot SSH eval (grading)

The autochecker bot SSHes into the VM, runs the agent, and evaluates.
Same stop-at-first-failure display. Uses 34 questions (25 shared + 9 extras).

```
SSH → cd ~/se-toolkit-lab-6 && python agent.py "..."
```

The 9 extra questions are never served by the API — students can only
encounter them through the bot. This prevents hard-coding answers.

**Display:**

```
Agent Evaluation: 25/34 passed

  ✅ What does REST stand for?
  ✅ What does ETL stand for?
  ✅ ...
  (24 more green)

  ❌ What is the average score for lab-04?
     Your answer: "I don't have access to the database"
     Expected: a number in range [0, 100]

Fix this question and re-run.
```

### 13.4 Logging

Every `/api/eval/question` request is logged:
- Student email
- Timestamp
- Question index
- Lab identifier

This gives us: progress per student, which questions are hardest
(highest index where students get stuck), iteration frequency.

---

## 14. Spec Structure (lab-06.yaml outline)

```yaml
tasks:
  - id: setup
    title: "Lab setup"
  - id: task-1
    title: "Task 1: Basic Agent Loop"
    prerequisite: setup
  - id: task-2
    title: "Task 2: Add Tools"
    prerequisite: task-1
  - id: task-3
    title: "Task 3: Pass the Benchmark"
    prerequisite: task-2

checks:
  # SETUP
  - repo_exists, repo_is_fork, repo_has_issues
  - ssh_connectivity (reuse from lab 5)
  - lab5_api_reachable (GET /docs returns 200)
  - lab5_has_data (GET /items/ returns non-empty with auth)

  # TASK 1
  - task1_issue_exists
  - task1_agent_cli_runs (SSH: python agent.py "hello" exits 0)
  - task1_output_valid_json (output has "answer" and "tool_calls" keys)
  - task1_basic_eval (tier 1 questions, ≥8/15)
  - task1_commit
  - task1_issue_has_linked_pr
  - task1_pr_approved

  # TASK 2
  - task2_issue_exists
  - task2_has_tools (read_file, list_files, query_api in code)
  - task2_tool_eval (tier 2 questions, ≥7/12)
  - task2_commit
  - task2_issue_has_linked_pr
  - task2_pr_approved

  # TASK 3
  - task3_issue_exists
  - task3_full_eval (all questions, ≥26/34)
  - task3_commit
  - task3_issue_has_linked_pr
  - task3_pr_approved
```

---

## 15. Decisions Made

| # | Question | Decision |
|---|----------|----------|
| 1 | Starter `agent.py` skeleton? | **No** — students build from scratch, plan first |
| 2 | Eval set versioned / rotated? | No for v1 — one fixed set |
| 3 | LLM rate limiting during eval? | Retry with backoff, count timeouts as fails |
| 4 | Tool call verification strict or loose? | Loose — check tool was used, not exact args |
| 5 | `query_db` (direct SQL) tool? | **No** — `query_api` is sufficient and safer |
| 6 | Max agent loop iterations? | **10** tool calls per question |
| 7 | Share example questions? | Not decided yet — leaning yes (small tier 1 sample) |
| 8 | Lab repo name? | **`se-toolkit-lab-6`** — confirmed |
| 9 | Agent code lives where? | **New repo** (`se-toolkit-lab-6`), not in lab 5 repo |
| 10 | Time estimate? | ~5-6 hours — not yet validated |
| 11 | Input format? | **Plain string argument** (`python agent.py "..."`) — not JSON |
| 12 | API key naming? | **`LMS_API_KEY`** (backend) vs **`LLM_API_KEY`** (LLM provider) |
| 13 | LLM config file? | **`.env.agent.secret`** (gitignored), with `.env.agent.example` committed |
| 14 | Task format? | **Deliverable-focused** (WHAT not HOW), 5 deliverables per task |

## 16. Remaining Work

- [x] Write Task 1 (Basic Agent Loop) — `lab/tasks/required/task-1.md`
- [x] Write Task 2 (Add Tools) — `lab/tasks/required/task-2.md`
- [x] Write Task 3 (Pass the Benchmark) — `lab/tasks/required/task-3.md`
- [x] Create question bank YAML v2 (`autochecker/specs/lab-06-eval.yaml`)
- [x] Implement eval API endpoint (`GET /api/eval/question` in dashboard)
- [x] Implement `run_eval.py` (shipped in lab repo)
- [x] Update README with lab story and learning advice
- [x] Deploy autochecker with eval endpoint
- [x] Create autochecker spec (`autochecker/specs/lab-06.yaml`)
- [x] Implement `agent_eval` check type in autochecker engine
- [x] Clean up old lab 5 content from `optional/task-1.md`
- [x] Update `instructors/lab-plan.md` in submodule to match final design
