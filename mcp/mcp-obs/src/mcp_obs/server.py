"""Observability MCP server — VictoriaLogs + VictoriaTraces tools."""

import os
from datetime import datetime, timezone

import httpx
from mcp.server.fastmcp import FastMCP

VICTORIALOGS_URL = os.environ.get("NANOBOT_VICTORIALOGS_URL", "http://victorialogs:9428")
VICTORIATRACES_URL = os.environ.get("NANOBOT_VICTORIATRACES_URL", "http://victoriatraces:10428")

mcp = FastMCP("observability")


@mcp.tool()
async def logs_search(query: str = "", service: str = "", severity: str = "", limit: int = 20, minutes: int = 60) -> str:
    """Search VictoriaLogs for log entries.

    Args:
        query: Free-text LogsQL query (e.g. 'service.name:"Learning Management Service"').
        service: Filter by service name (e.g. 'Learning Management Service').
        severity: Filter by severity (e.g. 'ERROR', 'INFO', 'WARN').
        limit: Maximum number of log entries to return.
        minutes: Time window in minutes (default 60).
    """
    parts = []
    if query:
        parts.append(query)
    if service:
        parts.append(f'service.name:"{service}"')
    if severity:
        parts.append(f"severity:{severity}")
    parts.append(f"_time:{minutes}m")
    full_query = " ".join(parts) if parts else f"_time:{minutes}m"

    url = f"{VICTORIALOGS_URL}/select/logsql/query"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, params={"query": full_query, "limit": limit}, timeout=15)
        resp.raise_for_status()
        lines = resp.text.strip().split("\n") if resp.text.strip() else []

    if not lines:
        return f"No log entries found for query: {full_query}"

    results = []
    for line in lines[:limit]:
        results.append(line)
    return "\n".join(results)


@mcp.tool()
async def logs_error_count(service: str = "", minutes: int = 60) -> str:
    """Count error-level log entries per service over a time window.

    Args:
        service: Filter by service name (e.g. 'Learning Management Service').
        minutes: Time window in minutes (default 60).
    """
    query = f"severity:ERROR _time:{minutes}m"
    if service:
        query = f'service.name:"{service}" severity:ERROR _time:{minutes}m'

    url = f"{VICTORIALOGS_URL}/select/logsql/query"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, params={"query": query, "limit": 1000}, timeout=15)
        resp.raise_for_status()
        lines = resp.text.strip().split("\n") if resp.text.strip() else []

    count = len([l for l in lines if l.strip()])
    svc_info = f' for service "{service}"' if service else ""
    return f"Found {count} error-level log entries{svc_info} in the last {minutes} minutes."


@mcp.tool()
async def traces_list(service: str = "", limit: int = 10) -> str:
    """List recent traces from VictoriaTraces.

    Args:
        service: Filter by service name (e.g. 'Learning Management Service').
        limit: Maximum number of traces to return.
    """
    url = f"{VICTORIATRACES_URL}/select/jaeger/api/traces"
    params: dict = {"limit": limit}
    if service:
        params["service"] = service

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

    traces = data.get("data", [])
    if not traces:
        return f"No traces found{f' for service \"{service}\"' if service else ''}."

    results = []
    for t in traces[:limit]:
        trace_id = t.get("traceID", "unknown")
        spans = t.get("spans", [])
        svc_names = set(s.get("process", {}).get("serviceName", "") for s in spans)
        results.append(f"trace_id: {trace_id} | services: {', '.join(svc_names)} | spans: {len(spans)}")
    return "\n".join(results)


@mcp.tool()
async def traces_get(trace_id: str) -> str:
    """Fetch a specific trace by ID from VictoriaTraces.

    Args:
        trace_id: The trace ID to fetch.
    """
    url = f"{VICTORIATRACES_URL}/select/jaeger/api/traces/{trace_id}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()

    traces = data.get("data", [])
    if not traces:
        return f"No trace found with ID: {trace_id}"

    t = traces[0]
    spans = t.get("spans", [])
    results = [f"Trace {trace_id} — {len(spans)} spans:"]
    for s in spans:
        op = s.get("operationName", "")
        svc = s.get("process", {}).get("serviceName", "")
        dur = s.get("duration", 0)
        tags = s.get("tags", [])
        errors = [tag for tag in tags if tag.get("key") == "error" and tag.get("value")]
        status = "ERROR" if errors else "ok"
        results.append(f"  [{status}] {svc} — {op} ({dur/1000:.1f}ms)")
    return "\n".join(results)
