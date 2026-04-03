---
name: observability
description: Use observability MCP tools to query logs and traces
always: true
---

# Observability Skill

You have access to observability tools that can query logs and traces from the LMS system.

## Available Tools

### Log tools (VictoriaLogs)
- `logs_search` — search logs by query, service, severity, and time range
- `logs_error_count` — count error-level log entries per service over a time window

### Trace tools (VictoriaTraces)
- `traces_list` — list recent traces for a service
- `traces_get` — fetch a specific trace by ID with span details

## Strategy

### When the user asks about errors or system health:

1. **Start with `logs_error_count`** — check if there are recent errors
   - Use a narrow time window (10-30 minutes) for fresh data
   - Filter by service name if the user mentions a specific service

2. **If errors found, use `logs_search`** — inspect the actual error messages
   - Filter by `severity:ERROR` and the relevant service
   - Look for `trace_id` fields in the log entries

3. **If trace_id found, use `traces_get`** — fetch the full trace
   - This shows the complete request flow across services
   - Identify which span failed and why

4. **Summarize findings concisely** — don't dump raw JSON
   - Report the number of errors, what services were affected
   - Explain the failure path if a trace shows an error
   - Keep responses focused on what the user asked about

### Example reasoning flow:

User: "Any LMS backend errors in the last 10 minutes?"

1. Call `logs_error_count(service="Learning Management Service", minutes=10)`
2. If count > 0, call `logs_search(service="Learning Management Service", severity="ERROR", minutes=10)`
3. Extract any `trace_id` from the error logs
4. Call `traces_get(trace_id="<extracted>")` to see the full failure path
5. Summarize: "Found X errors in the last 10 minutes. The errors show [brief description]. The trace reveals [failure point]."

### When no errors found:

Report clearly: "No errors found in the LMS backend logs in the last X minutes. The system appears healthy."

---

## Investigation Flow: "What went wrong?" or "Check system health"

When the user asks **"What went wrong?"** or **"Check system health"**, follow this investigation flow:

1. **Check for recent errors** — call `logs_error_count` with a narrow window (5-10 minutes)
   - If no errors: report the system looks healthy
   - If errors found: proceed to step 2

2. **Inspect error details** — call `logs_search` scoped to the failing service
   - Use `severity:ERROR` and the relevant service name
   - Look for error messages and any `trace_id` fields

3. **Fetch the trace** — if a `trace_id` is found in the logs, call `traces_get`
   - This reveals the full request flow and where it failed
   - Note which span has the error status

4. **Provide a coherent summary** that includes:
   - **Log evidence**: what the error logs show (error type, message, service affected)
   - **Trace evidence**: what the trace reveals (which span failed, the failure path)
   - **Root cause**: your assessment of what went wrong based on both sources
   - Keep it concise — one paragraph, not raw JSON dumps

### Example investigation:

User: "What went wrong?"

1. `logs_error_count(service="Learning Management Service", minutes=10)` → "Found 2 errors..."
2. `logs_search(service="Learning Management Service", severity="ERROR", minutes=10)` → shows `socket.gaierror` and `trace_id=abc123`
3. `traces_get(trace_id="abc123")` → shows db_query span failed with PostgreSQL connection error
4. Summary: "Found 2 errors in the LMS backend. Logs show a PostgreSQL connection failure (socket.gaierror). The trace confirms the db_query span failed when trying to connect to the database. The backend is unable to reach PostgreSQL."
