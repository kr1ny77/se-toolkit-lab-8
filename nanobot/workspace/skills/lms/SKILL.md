---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Skill

Use the LMS MCP tools to query live course data from the Learning Management System backend.

## Available Tools

- `mcp_lms_lms_health` — Check backend health and item count
- `mcp_lms_lms_labs` — List all available labs
- `mcp_lms_lms_pass_rates` — Get pass rates for a specific lab
- `mcp_lms_lms_scores` — Get scores for a specific lab
- `mcp_lms_lms_timeline` — Get submission timeline for a specific lab
- `mcp_lms_lms_groups` — Get group performance for a specific lab
- `mcp_lms_lms_completion_rate` — Get completion rate for a specific lab
- `mcp_lms_lms_top_learners` — Get top learners for a specific lab
- `mcp_lms_lms_learners` — Get list of learners
- `mcp_lms_lms_sync_pipeline` — Trigger data sync from autochecker API

## Strategy

### When the user asks about scores, pass rates, completion, groups, timeline, or top learners:

1. **If no lab is specified:**
   - Call `mcp_lms_lms_labs` first to get the list of available labs
   - Use `mcp_webchat_ui_message` with `type: "choice"` to let the user pick a lab
   - Use each lab's title as the label and the lab identifier as the value
   - Example labels: "Lab 01 – Products, Architecture & Roles", "Lab 02 — Run, Fix, and Deploy"

2. **If a lab is specified:**
   - Call the appropriate tool with the lab identifier
   - Format numeric results nicely:
     - Percentages: "75%" not "0.75"
     - Counts: "42 submissions" not "42"
   - Keep responses concise

### When the user asks "what can you do?" or about capabilities:

Explain your current tools and limits clearly:

```
I can help you query data from the Learning Management System:

- Check if the LMS backend is healthy
- List available labs
- Get pass rates, scores, and completion rates for a specific lab
- View submission timelines and group performance
- Find top learners in a lab

Just ask me about any of these, and I'll fetch the live data for you!
```

### When the backend health is unknown:

- Call `mcp_lms_lms_health` first to verify the backend is accessible
- If unhealthy, inform the user and suggest triggering a sync with `mcp_lms_lms_sync_pipeline`

## Response Style

- Keep responses concise and focused on the data
- Use bullet points for multiple metrics
- Highlight key numbers (pass rates, counts)
- When presenting lab choices, use the full lab title for clarity
- If a tool returns no data, say so clearly rather than hallucinating
