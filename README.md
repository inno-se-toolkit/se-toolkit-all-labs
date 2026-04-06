# Software Engineering Toolkit

Course syllabus for Software Engineering Toolkit at Innopolis University.

**Subject area:** Software Engineering

## P.1 Short Description

This course provides students with a foundational set of engineering skills needed to independently perform typical software development tasks, as well as hands-on experience with modern tools and technologies used in the industry. Students learn approaches to building software systems, working with code repositories, designing and implementing APIs, testing fundamentals, containerization, server deployment, integration with third-party APIs, and building user interfaces (web, bots, mobile applications).

**Main course concepts:**

- Software architecture: modules and deployment
- Version control with Git: branching, commits, pull requests, code review
- Backend development: REST API design, routing, request handling, data validation
- Testing: unit tests, end-to-end tests, boundary-value analysis
- Containerization with Docker and Docker Compose
- Database integration (PostgreSQL)
- Data pipelines (ETL), analytics dashboards
- AI/LLM integration: tool calling, agentic loops, MCP protocol
- Client interfaces: web dashboards, Telegram bots, Flutter apps

## P.2 Intended Learning Outcomes (ILOs)

### P.2.1 What is the purpose of this course?

The purpose of this course is to equip students with a foundational set of engineering skills for independently performing typical software development tasks — from individual development practices and server-side programming to testing, containerization, deployment, and integration of multiple components into a working prototype.

### P.2.2 ILOs defined at three levels

**Level 1: What concepts should a student know/understand/explain?**

By the end of the course, the students should be able to understand:

- The architectural principles of modern software systems
- Basic standards for API description and technical documentation
- Principles of REST, databases, containerization, and deployment
- Fundamentals of integrating third-party APIs and LLM services
- The Git workflow: issues, branches, pull requests, code review
- The role of testing (unit, E2E) and CI in software quality assurance

**Level 2: What practical skills should a student be able to perform?**

By the end of the course, the students should be able to:

- Use individual development tools (Git, Docker, databases)
- Develop and test server-side components (REST APIs)
- Design and implement API endpoints with proper error handling
- Deploy services in a server environment (Linux, Docker Compose)
- Build simple client interfaces (web dashboards, bots)

**Level 3: What comprehensive skills should a student be able to apply in real-life scenarios?**

By the end of the course, the students should be able to:

- Architect and deploy a multi-service application (backend + database + frontend)
- Integrate LLM/AI services into applications using tool calling and agentic patterns
- Build data pipelines (ETL) and analytics dashboards
- Containerize and deploy full-stack applications on remote servers
- Write technical documentation (README, API specs, deployment instructions)
- Work collaboratively using Git workflow with issues, PRs, and code review

## P.3 Course Sections and Labs

The course is organized into 4 sections delivered across 10 weekly labs.

| | Labs | Hours |
|---|---|---|
| 1. SE Fundamentals and Development Tools | Labs 1–2 | 8 |
| 2. Backend Development and Testing | Labs 3–4 | 8 |
| 3. Data, Containerization, and Service Integration | Labs 5–6 | 8 |
| 4. Client Interfaces, Analytics, and AI Agents | Labs 7–8 | 8 |
| 5. Hackathon + Demo Day | Labs 9–10 | 8 |
| **Labs total** | | **40** |
| Self-study | | 24 |
| Exam preparation | | 8 |
| **Course total** | | **72** |

### Labs

| Lab | Title | Repository |
|-----|-------|------------|
| 1 | Products, Architecture & Roles | [se-toolkit-lab-1](https://github.com/inno-se-toolkit/se-toolkit-lab-1) |
| 2 | Run, Fix, and Deploy a Backend Service | [se-toolkit-lab-2](https://github.com/inno-se-toolkit/se-toolkit-lab-2) |
| 3 | Backend API: Explore, Debug, Implement, Deploy | [se-toolkit-lab-3](https://github.com/inno-se-toolkit/se-toolkit-lab-3) |
| 4 | Testing, Front-end, and AI Agents | [se-toolkit-lab-4](https://github.com/inno-se-toolkit/se-toolkit-lab-4) |
| 5 | Data Pipeline and Analytics Dashboard | [se-toolkit-lab-5](https://github.com/inno-se-toolkit/se-toolkit-lab-5) |
| 6 | Build Your Own Agent | [se-toolkit-lab-6](https://github.com/inno-se-toolkit/se-toolkit-lab-6) |
| 7 | Build a Client with an AI Coding Agent | [se-toolkit-lab-7](https://github.com/inno-se-toolkit/se-toolkit-lab-7) |
| 8 | The Agent is the Interface | [se-toolkit-lab-8](https://github.com/inno-se-toolkit/se-toolkit-lab-8) |
| 9 | Hackathon | [se-toolkit-lab-9](https://github.com/inno-se-toolkit/se-toolkit-lab-9) |
| 10 | Demo Day | [se-toolkit-lab-10](https://github.com/inno-se-toolkit/se-toolkit-lab-10) |

### Section 1: SE Fundamentals and Development Tools

**Labs 1–2**

Topics covered:
- Architecture of modern digital products: modules, communications, deployment
- Engineering roles and essential skills
- Git fundamentals: branching, commits, pull requests, code review
- Task tracking with issues and kanban boards
- Technical documentation (README, bug reports, specifications)

**Evaluation:** Lab completion via autochecker bot; attendance during lab sessions.

### Section 2: Backend Development and Testing

**Labs 3–4**

Topics covered:
- Backend server development: project structure, routing, request handling
- REST API design: principles, conventions, errors, data validation
- Bug finding and fixing: issue tracking, bug reports, debugging
- Functional and unit testing; basic CI automation
- Deploying backend applications to a remote server (Linux, systemd, nginx)

**Evaluation:** Lab completion via autochecker bot; code review of pull requests; attendance during lab sessions.

### Section 3: Data, Containerization, and Service Integration

**Labs 5–6**

Topics covered:
- Docker and Docker Compose fundamentals
- Database schema design and application-DB interaction
- Containerizing backend services and databases
- Building and running multi-component applications
- Integration with third-party APIs or LLM services, error handling and logging

**Evaluation:** Lab completion via autochecker bot; deployed services verification on VM; attendance during lab sessions.

### Section 4: Client Interfaces, Analytics, and AI Agents

**Labs 7–8**

Topics covered:
- Building client interfaces (web, Telegram bot, Flutter app)
- Collecting analytics data: events, activity, logging
- Building analytics dashboards
- AI agent frameworks: nanobot, MCP tools, skill prompts, cron jobs
- Observability: structured logging, distributed tracing (VictoriaLogs, VictoriaTraces)
- Using AI agents to diagnose production issues

**Evaluation:** Lab completion via autochecker bot; deployed agent and client verification on VM; attendance during lab sessions.

## P.3.2 Theory Quiz Question Bank

See [docs/Question bank.md](docs/Question%20bank.md) for the full list of quiz questions covering:

- Git & Workflow (Q1–Q3)
- HTTP & REST API (Q4–Q7)
- Security & Authentication (Q8–Q10)
- Docker & Deployment (Q11–Q14)
- Testing (Q15–Q16)
- Data Pipelines (Q17)
- LLM Agents & Tool Use (Q18–Q19)
- Bot Architecture & Integration (Q20–Q21)
- System Design (Q22)

## P.3.3 The Retake Exam

For the retake, the student must:

1. **Pass all labs**
2. **Pass the theory quiz**
3. **Build and deploy a hackathon project**
4. **Present the results**

## P.4 Grading

### P.4.1 Pass/Fail

This is a **pass/fail** course. There are no letter grades.

**How to pass:**
- Accumulate **9 participation points** total (out of 10 labs), AND
- Attend and present at **Lab 10 (Demo Day)**

### P.4.2 Participation Scoring

The following rules apply across all labs, unless specified otherwise.

Participation means **attending** and **completing all required tasks**.

| Condition | Points |
|-----------|--------|
| Attended + completed all required tasks | 1.0 |
| Completed tasks without attendance | 0.5 |
| Did not complete required tasks | 0.0 |

- Required tasks are submitted via the autochecker bot ([@auchebot](https://t.me/auchebot))
- Deadline: **Thursday 23:59** following the lab

### P.4.3 Legal Excuses

Students with a legal excuse receive a deadline extension to submit in [@auchebot](https://t.me/auchebot).

The extension length equals the number of excused days, counted starting from the lab day. For example, if you have a legal excuse from Thursday to Tuesday and your lab is on Saturday, you get an extension of four days (Saturday to Tuesday).

Legal excuse information is collected from the Dean's Office (DoE) when finalizing the course.

### P.4.4 Recommendations for Students

1. Complete each lab on time. Labs build on each other — falling behind makes later labs harder.
2. Use the autochecker bot to verify your work before the deadline.
3. Follow the Git workflow: issues, branches, PRs with code review from a partner.
4. Deploy your services on the VM early. Most issues surface during deployment, not local development.
5. Read the wiki articles linked in each lab — they explain the concepts you need.
6. Use your AI coding agent (Qwen Code) as a development partner, but understand what it builds.

## P.5 Resources

### Open Access

- [GitHub course repositories](https://github.com/inno-se-toolkit)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Docker documentation](https://docs.docker.com/)
- [Git documentation](https://git-scm.com/doc)

### Course-Internal

- Course wiki (available within each lab repository)
- Autochecker bot and dashboard (Innopolis internal)

### Software and Tools

- Git, GitHub — version control and collaboration
- Docker, Docker Compose — containerization
- VS Code with Remote-SSH — development environment
- Python, uv — backend development
- PostgreSQL — database
- Qwen Code API — LLM proxy for AI agent labs
- Nanobot — AI agent framework (Labs 7–8)
