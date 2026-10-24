# LifeOps AI — Voice-first autonomous day planner

**Amazon Developer Hackathon | Alexa+ simulated-experience track**

LifeOps AI is a voice-first, Alexa+-style productivity assistant. Speak or type commands, create tasks, mark them complete, and generate a conflict-aware daily schedule. The dashboard updates when the agent executes real tools over **MCP Streamable HTTP**.

> **Disclosure:** This is an independently built simulated Alexa+ experience. It is **not connected to the official Alexa+ service** and does not require an Echo device or gated Alexa+ partner access.

## Features

- Browser speech-to-text (push-to-talk; Chrome recommended) and spoken responses (Web Speech API)
- Natural-language task actions, using a deterministic parser by default; optionally enhanced by an OpenAI API model
- Seven real MCP tools: `create_task`, `list_tasks`, `edit_task`, `remove_task`, `replan_schedule`, `save_preference`, `read_preferences`
- Persistent SQLite database
- Earliest-deadline-first planning, explicit conflict warnings, configurable work hours and breaks
- Responsive, dark-mode task dashboard with task completion, deletion and task entry
- No external account required; runs locally without an AI API key

## Architecture

```text
Browser (HTML/CSS/JS + Web Speech API)
    | REST requests (port 8001)
FastAPI web/API server (backend/api.py)
    | MCP Python client (tools/list + tools/call; port 8000)
FastMCP Streamable HTTP server (backend/mcp_server.py)
    | Python tool functions
SQLite persistence (backend/store.py) + planner (backend/planner.py)
```

The API agent uses the MCP client to invoke tools; it does not mutate the database directly. The optional OpenAI API performs command classification only; execution still goes through MCP. The demo works without any external API key using explicit phrases.

## Requirements

- Windows/macOS/Linux with Python **3.11+**
- Internet for first-time Python dependency installation
- Chrome or Edge for browser voice recognition (browser support varies; text fallback always works)

## Quick start — VS Code on Windows

Open a VS Code terminal in this repository:

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Terminal 1 — MCP server:**

```powershell
cd backend
.\.venv\Scripts\python.exe mcp_server.py
```

**Terminal 2 — web/API server:**

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn api:app --host 127.0.0.1 --port 8001
```

If you are already in the `backend` folder, don't run `cd backend` again. Open **http://127.0.0.1:8001** in Chrome and allow microphone access when prompted.

MCP endpoint: **http://127.0.0.1:8000/mcp**. This is a protocol endpoint, not a normal webpage.

### macOS/Linux

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
# Terminal 1:
.venv/bin/python mcp_server.py
# Terminal 2, from backend:
.venv/bin/python -m uvicorn api:app --host 127.0.0.1 --port 8001
```

## Demo commands

Without an AI key, use these exact patterns:

1. **“Add prepare interview high priority”** — creates a high-priority task.
2. **“Add finish hackathon submission”** — creates another task.
3. **“Show my tasks”** — reads saved tasks via MCP.
4. **“Plan my day”** — computes a schedule and flags tasks that don't fit.
5. **“Complete task 1”** — marks task ID 1 done.
6. **“Plan my day”** — updates the schedule without completed tasks.

You can also add deadlines via the task form. The default parser is intentionally limited: complex phrases such as “my interview moved to 8” require an optional model API key or manual editing. Never claim such parsing works in a demo without testing it.

### Optional AI parsing

Set `OPENAI_API_KEY` in **both** the environment of the API server process (not the browser). Example in PowerShell before starting the API server:

```powershell
$env:OPENAI_API_KEY="your_key_here"
$env:OPENAI_MODEL="gpt-4o-mini"
.\.venv\Scripts\python.exe -m uvicorn api:app --host 127.0.0.1 --port 8001
```

This is optional and **does not qualify for the AWS Builder mini challenge**. Never commit secrets. The classifier may be imperfect; review its task changes.

## How to verify MCP

With both servers running, visit `http://127.0.0.1:8001/api/health`, then open the dashboard and add a task. The API uses an actual MCP `ClientSession` and `call_tool` for task creation. You can also inspect the MCP server with an MCP-compatible inspector/client supporting Streamable HTTP at `http://127.0.0.1:8000/mcp`.

## Limitations and safety

- No real Alexa+ or Echo connection; web simulation only.
- Push-to-talk, not always-listening or “Alexa” wake-word activation.
- Browser speech recognition may depend on browser/network and may be unavailable; type commands as fallback.
- Single-user local MVP, no authentication or multi-tenant isolation. Do not expose to the public internet without authentication and MCP security hardening.
- SQLite task data is stored locally. No Google Calendar or other external calendar integration.
- Scheduling uses sequential blocks within working hours, not a full constraint solver. It may flag tasks with impossible deadlines.
- Date/time uses the backend computer's local timezone.
- Optional external model calls send task titles and user messages to the configured model provider; use only non-sensitive demo data.

## Repository / judging

Public repository: retain the `LICENSE` file. For a private repository, follow Devpost's reviewer-access instructions. Record a **public, English-language video under 3 minutes** showing the actual running app and explain it is an Alexa+-style simulation. Include honest product feedback and any genuine friction log entries. Do not claim AWS Builder unless you integrate qualifying AWS technology.

## Source layout

```text
backend/api.py         FastAPI HTTP server and static UI hosting
backend/agent.py       Intent parsing, optional LLM, MCP client tool calls
backend/mcp_server.py  FastMCP Streamable HTTP tools
backend/planner.py     Conflict-aware deterministic scheduling
backend/store.py       SQLite storage
frontend/index.html    Accessible single-page UI
frontend/styles.css    Responsive styling
frontend/app.js        Chat, voice, dashboard interactions
docs/SUBMISSION.md     Submission copy and demo outline
```


## OpenRouter configuration (recommended)

OpenRouter lets LifeOps AI use OpenAI models with an OpenRouter API key (no separate OpenAI key).

1. From `backend`, copy `.env.example` to `.env`: PowerShell `Copy-Item .env.example .env`.
2. In `.env`, set `OPENROUTER_API_KEY=your_key` and `OPENROUTER_MODEL=openai/gpt-4o-mini`. Do not share or commit `.env`.
3. Install requirements: `python -m pip install -r requirements.txt`.
4. Start `python mcp_server.py` in one terminal, and `python -m uvicorn api:app --host 127.0.0.1 --port 8001` in another.
5. Open `http://127.0.0.1:8001` and try `Add prepare presentation tomorrow at 4 PM, high priority`.

OpenRouter charges according to the selected model. The app silently falls back to rule-based parsing if the API request fails; check your OpenRouter usage dashboard if natural-language requests behave like basic commands.
<img width="1907" height="855" alt="Pro1" src="https://github.com/user-attachments/assets/64cb42d3-1250-47e4-b498-e9cc62c0a266" />
<img width="1912" height="862" alt="Pro2" src="https://github.com/user-attachments/assets/9856ff49-8351-47f4-acfc-500cb069b36b" />
<img width="1912" height="862" alt="Pro3" src="https://github.com/user-attachments/assets/c8798ade-d763-4b6f-87ce-dbc142d27854" />



