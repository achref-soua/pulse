# Pulse MCP Server

Pulse exposes its clinical decision-support capabilities as a [Model Context Protocol](https://modelcontextprotocol.io) server, so external AI agents (or your own assistant) can drive Pulse programmatically. The server is a thin adapter over the same grounded tool layer the in-app agent uses ([ADR-0009](adr/0009-mcp-server-shares-tool-layer.md)) — scores come from the tested calculators, never estimated.

> Educational demo on synthetic data — not for clinical use; not medical advice.

## Running it

Over stdio (the transport MCP clients expect):

```bash
task mcp
# or, from apps/api:
uv run python -m app.mcp
```

It reuses the API's configuration, so `DATABASE_URL` must point at a seeded Pulse database. `search_guidelines` additionally uses the embedding model + Quiver and degrades to an empty result if Quiver is unreachable.

## Tools

| Tool | Description |
|------|-------------|
| `calculate_risk_score(kind, inputs)` | Compute a validated score (`rcri`, `cha2ds2_vasc`, `has_bled`, `news2`, `gas`, `euroscore2`) from explicit inputs. |
| `score_patient(patient_id)` | Every applicable score for a patient, inputs derived server-side from the chart. |
| `get_patient(patient_id)` | Structured record: demographics, aortic anatomy, comorbidities, vitals. |
| `match_devices(patient_id)` | Rank the stent-graft catalog against the patient's anatomy (IFU-fit engine). |
| `search_guidelines(query)` | Semantic search over the guidelines + literature knowledge base. |
| `query_cohort(filters)` | Count and break down the cohort by structured filters. |

## Connecting a client

Point any MCP-capable client at the stdio command. For Claude Desktop, add to its config:

```json
{
  "mcpServers": {
    "pulse": {
      "command": "uv",
      "args": ["run", "python", "-m", "app.mcp"],
      "cwd": "/path/to/pulse/apps/api"
    }
  }
}
```

The agent can then ask, e.g., "score patient P001 and check EVAR suitability", and Pulse answers with grounded, deterministic results.
