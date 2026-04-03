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
