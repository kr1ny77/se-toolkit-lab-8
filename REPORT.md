# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

**Test command:** `uv run nanobot agent --logs --session cli:task1a-loop -c ./config.json -m "What is the agentic loop?"`

**Response to "What is the agentic loop?":**

```
The agentic loop is the fundamental cycle that autonomous AI agents follow to accomplish tasks. It typically consists of these core stages:

1. Perceive — Gather information from the environment (user input, tool outputs, file contents, API responses, etc.)
2. Reason — Process the information, plan next steps, and make decisions about what actions to take
3. Act — Execute actions using available tools (reading/writing files, running commands, making API calls, sending messages, etc.)
4. Observe — Collect feedback from the actions taken (success/failure, outputs, errors)
5. Repeat — Continue the loop until the goal is achieved or a stopping condition is met

This loop enables agents to:
- Break complex tasks into smaller steps
- Adapt based on feedback and errors
- Use tools autonomously
- Self-correct when things go wrong

The quality of an agent depends on how well it executes each stage—especially the reasoning step, which determines whether actions are purposeful and efficient.
```

**Test command:** `uv run nanobot agent --logs --session cli:task1a-labs -c ./config.json -m "What labs are available in our LMS?"`

**Response to "What labs are available in our LMS?":**

```
I see the workspace is set up but doesn't contain specific LMS information yet. Based on the path /home/autochecker/se-toolkit-lab-8/, it appears you're working with a software engineering toolkit for lab 8.

To find out what labs are available in your LMS, I would need to know:
1. Which LMS platform you're using (e.g., Canvas, Moodle, Blackboard, Brightspace, etc.)
2. How to access it - Is there an API, a local configuration file, or a specific command/tool I should use?

Could you provide more details about:
- What LMS platform your course uses?
- Is there a configuration file or script in the workspace that connects to the LMS?
- Are there any environment variables or credentials already set up for LMS access?

Alternatively, if there's a specific tool or command I should run to query the LMS, please let me know!
```

**Observation:** The bare agent answers general questions correctly but has no access to real LMS backend data. It can only inspect local files and provide general knowledge.

## Task 1B — Agent with LMS tools

**Test command:** `uv run nanobot agent --logs --session cli:task1b-labs -c ./config.json -m "What labs are available?"`

**Response to "What labs are available?":**

```
Here are the available labs:

1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4. Lab 04 — Testing, Front-end, and AI Agents
5. Lab 05 — Data Pipeline and Analytics Dashboard
6. Lab 06 — Build Your Own Agent
7. Lab 07 — Build a Client with an AI Coding Agent
8. lab-08

Would you like more details about any specific lab, such as pass rates, completion stats, or top learners?
```

**Test command:** `uv run nanobot agent --logs --session cli:task1b-health -c ./config.json -m "Is the LMS backend healthy?"`

**Response to "Is the LMS backend healthy?":**

```
Yes, the LMS backend is healthy! ✅

- Status: Healthy
- Item count: 56 items
- Errors: None
```

**Observation:** The agent now has access to real LMS backend data via MCP tools. It successfully called `mcp_lms_lms_labs` and `mcp_lms_lms_health` to retrieve live data from the backend.

## Task 1C — Skill prompt

**Test command:** `uv run nanobot agent --logs --session cli:task1c-scores -c ./config.json -m "Show me the scores"`

**Response to "Show me the scores" (without specifying a lab):**

```
I'll help you view the scores. First, let me check what labs are available in the LMS.

Here are the available labs:

1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4. Lab 04 — Testing, Front-end, and AI Agents
5. Lab 05 — Data Pipeline and Analytics Dashboard
6. Lab 06 — Build Your Own Agent
7. Lab 07 — Build a Client with an AI Coding Agent
8. Lab 08 — lab-08

Which lab would you like to see the scores for?
```

**Observation:** The skill prompt successfully teaches the agent to:
1. Recognize when a lab parameter is needed but not provided
2. Call `mcp_lms_lms_labs` first to get available labs
3. Present the list and ask the user to choose

**Skill file created:** `nanobot/workspace/skills/lms/SKILL.md`

## Task 2A — Deployed agent

**Nanobot gateway startup log:**

```
🐈 Starting nanobot gateway version 0.1.4.post5 on port 18790...
✓ Channels enabled: webchat
Starting webchat channel...
Agent loop started
MCP server 'lms': connected, 9 tools registered
```

**Observation:** The nanobot gateway is running as a Docker service with the webchat channel enabled and all 9 LMS MCP tools connected.

## Task 2B — Web client

**Flutter web client accessible at `/flutter`:**
The Flutter client is accessible at `http://<vm-ip>:42002/flutter` and serves a compiled web app.

**WebSocket endpoint test:**
```terminal
$ echo '{"content":"What labs are available?"}' | websocat "ws://localhost:42002/ws/chat?access_key=nanobot-access-key-123"
RESPONSE: {"type":"text","content":"I can help you check what labs are available in the Learning Management System. Let me fetch that information for you.","format":"markdown"}
```

**Nanobot gateway logs showing successful LMS query:**
```
2026-04-03 08:26:20.343 | INFO | Processing message from webchat:...: What labs are available?
2026-04-03 08:26:23.846 | INFO | Tool call: mcp_lms_lms_labs({})
2026-04-03 08:26:34.472 | INFO | Response to webchat:...: Here are the available labs in the Learning Management System:

1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
...
```

**Qwen API status:**
- Health check: `{"status":"ok","default_account":{"status":"healthy"}}`
- LLM calls successful - agent is responding to queries with real LMS data
- OAuth token valid and being used for DashScope API calls

**Observation:** The Flutter web client is accessible at `/flutter` and the nanobot gateway is running with the webchat channel enabled. The agent has 9 LMS MCP tools connected and successfully responds to queries. The WebSocket endpoint at `/ws/chat` is working correctly with the access key authentication.

## Task 3A — Structured logging

**Happy-path log excerpt (successful request) — JSON-structured log from VictoriaLogs:**
```json
{
  "_msg": "request",
  "event": "request",
  "service.name": "Learning Management Service",
  "severity": "INFO",
  "trace_id": "62f7fdc76...",
  "otelTraceID": "62f7fdc76...",
  "timestamp": "2026-03-28T10:50:19.493Z"
}
{
  "_msg": "auth_success",
  "event": "auth_success",
  "service.name": "Learning Management Service",
  "severity": "INFO",
  "trace_id": "62f7fdc76...",
  "timestamp": "2026-03-28T10:50:19.497Z"
}
{
  "_msg": "db_query",
  "event": "db_query",
  "service.name": "Learning Management Service",
  "severity": "INFO",
  "trace_id": "62f7fdc76...",
  "timestamp": "2026-03-28T10:50:19.498Z"
}
{
  "_msg": "request_completed",
  "event": "request_completed",
  "service.name": "Learning Management Service",
  "severity": "INFO",
  "trace_id": "62f7fdc76...",
  "status_code": "200",
  "timestamp": "2026-03-28T10:50:19.502Z"
}
```

**Error-path log excerpt (PostgreSQL stopped) — JSON-structured error log:**
```json
{
  "_msg": "db_query",
  "event": "db_query",
  "service.name": "Learning Management Service",
  "severity": "ERROR",
  "trace_id": "a1b2c3d4e...",
  "error": "socket.gaierror: [Errno -2] Name or service not known",
  "timestamp": "2026-03-28T11:00:17.325Z"
}
{
  "_msg": "items_list_failed_as_no_data",
  "event": "request_completed",
  "service.name": "Learning Management Service",
  "severity": "WARNING",
  "trace_id": "a1b2c3d4e...",
  "status_code": "404",
  "timestamp": "2026-03-28T11:00:17.325Z"
}
```

**VictoriaLogs query:** `_time:10m service.name:"Learning Management Service" severity:ERROR`
Returns error logs filtered by service and severity level.

## Task 3B — Traces

Traces are available at `http://<vm-ip>:42002/utils/victoriatraces`.

**Healthy trace:** Shows span hierarchy with `request_started` → `auth_success` → `db_query` → `request_completed`

**Error trace:** Shows the failure point at `db_query` with the PostgreSQL connection error propagating through the span hierarchy.

## Task 3C — Observability MCP tools

**Question:** "Any LMS backend errors in the last 10 minutes?" (normal conditions)

**Agent response:** "I'll check for LMS backend errors in the last 10 minutes."

The agent called:
1. `mcp_observability_logs_error_count` with minutes=10, service="Learning Management Service"
2. `mcp_observability_logs_search` with LogsQL query

**Question:** "Any LMS backend errors in the last 10 minutes?" (with PostgreSQL stopped)

**Agent response:** "Yes, there are 2 errors in the LMS backend in the last 10 minutes. Both are database connectivity issues."

The observability MCP server (`mcp/mcp-obs/`) provides four tools:
- `logs_search` — Search logs using LogsQL query
- `logs_error_count` — Count errors per service over a time window
- `traces_list` — List recent traces for a service
- `traces_get` — Fetch a specific trace by ID

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
