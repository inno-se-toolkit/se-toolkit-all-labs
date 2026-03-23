# SE Toolkit — Theory Quiz: Question Bank

## Git & Workflow

**Q1.** Describe a good Git/GitHub workflow for a lab task from start to finish. What happens at each stage?

> Expect: issue, branch, commit, pull request, review, merge.

**Q2.** You and a teammate both edited the same line in `README.md` on separate branches. What will this lead to? Describe step-by-step how you resolve it.

**Q3.** What is a conventional commit message? Give an example of a correct conventional commit for a bug fix to the login endpoint, and explain why teams adopt this convention.

---

## HTTP & REST API

**Q4.** Describe the main parts of an HTTP request and an HTTP response.

> Expect: method, path, query parameters, headers, body, status code, and response body.

**Q5.** A client calls an API and receives HTTP 200, 403, 404, or 500. Explain what each status code usually means, and what kind of problem (if any) you would suspect first in each case.

**Q6.** You open Swagger UI for an unfamiliar API and have 10 minutes to understand how to use it. What specific information can you extract from Swagger UI, and how does it help you treat the API as a contract between frontend and backend?

> Expect: endpoints, methods, parameters, authentication, request/response bodies and formats; Swagger acts as a live, testable contract that both sides agree on.

**Q7.** What is the relationship between a database schema, a model object, and business logic? What will a mismatch between them lead to and why?

---

## Security & Authentication

**Q8.** Compare API-key authentication and username/password authentication. How does each work, what is each commonly used for, and what are the main tradeoffs?

**Q9.** Explain the difference between *authentication* and *authorization*. 

**Q10.** You SSH into your VM and need to harden it. Name four specific security measures you would apply and explain why each matters.

> Expect: firewall rules, fail2ban, disabling root SSH login, and disabling password authentication.

---

## Docker & Deployment

**Q11.** Explain three ways we deployed our LMS service locally and on VM. What does each stage add, and why do we use all three?

> Expect: venv with uv, Docker Compose locally, and Docker Compose on a remote VM.

**Q12.** Explain the difference between a `Dockerfile` and a `docker-compose.yml` file. What problem does each solve, and how do they relate to each other?

**Q13.** What is *Docker layer caching*? Given this Dockerfile:

```dockerfile
FROM python:3.12-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

You change one line in `main.py` and rebuild. Explain why *all* layers from `COPY` onward are rebuilt, and rewrite the Dockerfile so that changing `main.py` does **not** reinstall dependencies.

**Q14.** What is the *build context* in Docker? A student's image is 2 GB even though the app is 50 MB. They run `docker build .` from a directory that also contains `.git/`, `node_modules/`, and training data. Explain what happened and how to fix it.

---

## Testing

**Q15.** What is the difference between a *unit test* and an *end-to-end (E2E) test*? Describe what kinds of bugs each is designed to catch. Give one advantage and one disadvantage of each.

**Q16.** Define *boundary-value analysis*. For a function `get_grade(score: int)` that returns "F" for 0–49, "C" for 50–74, "B" for 75–89, and "A" for 90–100, list the specific boundary values you would test.

---

## Data Pipelines

**Q17.** Explain what an *ETL pipeline* is (what each letter stands for and means). In the context of syncing data from an external API to a local PostgreSQL database, give a concrete example of what happens in each stage.

---

## LLM Agents & Tool Use

**Q18.** Describe the agentic loop step by step, from user input to final answer. Include what happens when the LLM requests a tool call.

**Q19.** Your agent is asked *"How many endpoints does the API have?"* It has two tools: `read_file` and `list_files`. The agent calls `read_file("main.py")` once and answers "3 endpoints," but the correct answer is 7 (routes are spread across multiple files). What went wrong and how would you improve the agent's behavior?

---

## Bot Architecture & Integration

**Q20.** You want to test your Telegram bot's logic without sending real Telegram messages. How would you design the bot's code so that this is possible?

> Expect: separate handlers (business logic) from transport (Telegram); use CLI `--test` mode or call handlers directly in tests.

**Q21.** In Lab 7, user messages are routed to backend API calls using an LLM instead of regex/command matching. Give one advantage and one disadvantage of LLM-based intent routing compared to traditional command parsing (e.g., `/scores lab-03`).

> Expect: user message → tool definitions → LLM decision → tool execution → feeding results back → final response.

---

## System Design

**Q22.** Draw and describe the full architecture of the LMS system we built across labs 2–7. Include all components (backend, database, bot, LLM, external APIs), show how they communicate, and explain how the system is deployed (what runs where and how).

> Expect: FastAPI backend + PostgreSQL on VM via Docker Compose; Telegram bot service calling backend API; LLM API (OpenRouter/Qwen) for agent and intent routing; ETL sync from external API; deployment via Docker Compose on remote VM; diagram showing containers, network connections, and external services.
