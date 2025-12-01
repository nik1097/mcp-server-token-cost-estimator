# mcp-server-cost-estimator

Token cost estimator for MCP (Model Context Protocol) servers.

## Installation

```bash
uv pip install -e .
```

## Usage

Estimate token costs for MCP tool calls:

```bash
uv run mcp-tok <server-url> --token <auth-token> [OPTIONS]
```

### Options

- `--tool <name>`: Test a specific tool (omit to test all tools)
- `--sample <json>`: Provide sample input as JSON string
- `--token, -t <token>`: Bearer token for authentication

### Examples

**List all tools and estimate token costs:**
```bash
uv run mcp-tok https://mcp.morningstar.com/mcp --token YOUR_TOKEN
```

**Test a specific tool:**
```bash
uv run mcp-tok https://mcp.morningstar.com/mcp \
  --token YOUR_TOKEN \
  --tool morningstar-id-lookup-tool
```

**Test with sample input:**
```bash
uv run mcp-tok https://mcp.morningstar.com/mcp \
  --token YOUR_TOKEN \
  --tool morningstar-id-lookup-tool \
  --sample '{"investments": [{"investment_name": "Apple Inc"}]}'
```

## Output

Returns JSON with token counts for each tool call:

```json
{
  "server": "https://mcp.morningstar.com/mcp",
  "results": [
    {
      "tool": "morningstar-id-lookup-tool",
      "tokens": 245
    }
  ]
}
```

## Protocol

Uses MCP over HTTP with Server-Sent Events (SSE) transport and JSON-RPC 2.0.
