# mcp-server-cost-estimator

Token cost estimator for MCP (Model Context Protocol) servers.

## Installation

```bash
uv pip install -e .
```

## Usage

```bash
uv run mcp-tok <server-url> --tools-config <config-file> [OPTIONS]
```

### Options

- `--tools-config, -t`: Path to JSON file specifying tools and their input parameters
- `--token`: Bearer token for authentication
- `--cost, -c`: Cost per million input tokens (e.g., 2.50 for $2.50/1M tokens)

### Tools Config File

Create a JSON file mapping tool names to their input parameters. Each tool can have different inputs.

**Example `tools.json`:**
```json
{
  "id-lookup-tool": {
    "investments": [{"investment_name": "Apple"}]
  },
  "data-fetch-tool": {
    "investment_ids": ["ABC123XYZ"],
    "d_ids": ["DP_001"]
  },
  "data=create-tool": {
    "investment_ids": ["FUND456DEF"],
    "num_points": 10
  }
}
```

**For tools with no required parameters, use an empty object:**
```json
{
  "tool-with-no-params": {},
  "another-tool": {
    "param1": "value1"
  }
}
```

### Examples

**Basic usage:**
```bash
uv run mcp-tok https://mcp.morningstar.com/mcp \
  --tools-config tools.json \
  --token YOUR_TOKEN
```

**With cost estimation:**
```bash
uv run mcp-tok https://mcp.morningstar.com/mcp \
  --tools-config tools.json \
  --token YOUR_TOKEN \
  --cost 2.50
```

**Test all available tools (no config needed):**
```bash
uv run mcp-tok https://mcp.morningstar.com/mcp --token YOUR_TOKEN
```

## Output

Console output shows token counts and costs per tool:
```
[morningstar-id-lookup-tool] tokens = 245 | cost = $0.000613
[morningstar-data-tool] tokens = 1823 | cost = $0.004558
```

Final JSON summary:
```json
{
  "server": "https://mcp.morningstar.com/mcp",
  "results": [
    {"tool": "morningstar-id-lookup-tool", "tokens": 245},
    {"tool": "morningstar-data-tool", "tokens": 1823}
  ]
}
```
