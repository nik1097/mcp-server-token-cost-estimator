# mcp-server-token-cost-estimator

Have you ever wondered what a single response from a tool on an MCP server would cost you based on the model you’re using? Tool responses are basically tokens, and these tokens end up as input tokens for the LLM, which costs money. Since MCP servers push the LLM inference cost back to the client, it’s important for the client to know if an MCP server is not only bloating the context but also getting expensive to run.

Some MCP server tools return way too much information just to answer your query. This repo helps you check that cost. Whether you’re a developer building an MCP server or a client trying to understand the cost of different requests, this tool helps you estimate how much each request might cost based on the model and cost multiplier you provide.

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
- `--provider, -p`: Token counting provider: `openai` (default) or `claude`
- `--claude-base-url`: Base URL for Claude API (required if provider=claude)
- `--claude-api-key`: API key for Claude (required if provider=claude)
- `--claude-model`: Claude model name for token counting (default: claude-sonnet-4-5)

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

**Basic usage with OpenAI (default):**
```bash
uv run mcp-tok https://mcp.morningstar.com/mcp \
  --tools-config tools.json \
  --token YOUR_TOKEN
```

**With Claude token counting:**
```bash
uv run mcp-tok https://mcp.morningstar.com/mcp \
  --tools-config tools.json \
  --token YOUR_TOKEN \
  --provider claude \
  --claude-base-url https://your-azure-endpoint.com/anthropic \
  --claude-api-key YOUR_CLAUDE_KEY \
  --cost 3.0
```

**With cost estimation (OpenAI):**
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

## Provider Comparison

### OpenAI (default)
- Uses `tiktoken` with `o200k_base` encoding
- Fast, offline token counting
- Approximates OpenAI models (GPT-4, GPT-4o, etc.)
- Does not require API calls

### Claude
- Uses Anthropic's official `count_tokens` API
- Accurate token counting for Claude models
- Requires API credentials and makes API calls
- Supports tool definitions in token count
- Recommended when using Claude models (Sonnet, Opus, Haiku)

**Note:** Token counts may differ between providers due to different tokenization methods. Use the provider that matches your LLM choice for accurate cost estimates.
