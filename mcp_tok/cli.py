import json
import typer
from typing import Optional
from .client import MCPClient
from .tokenizer import Tokenizer

app = typer.Typer(help="MCP Cost Estimator CLI")


@app.command()
def estimate(
    server_url: str = typer.Argument(..., help="Base URL of the MCP server"),
    tool: Optional[str] = typer.Option(None, help="Specific tool to call"),
    sample: Optional[str] = typer.Option(None, help="JSON string with sample payload"),
    token: Optional[str] = typer.Option(
        None,
        "--token",
        "-t",
        help="Bearer token for MCP server authentication",
    ),
    cost_per_million: Optional[float] = typer.Option(
        None,
        "--cost",
        "-c",
        help="Cost per million input tokens (e.g., 3.0 for $3.00/1M tokens)",
    ),
):
    """
    Estimate token cost for one or all MCP tools by calling them directly.
    No LLMs involved — raw HTTP only.
    """
    client = MCPClient(server_url, token=token)
    tokenizer = Tokenizer()

    # Load all tools or a specific tool
    if tool:
        tools = [tool]
    else:
        tools_meta = client.get_tools()
        # The response should have a "tools" key containing the list
        if isinstance(tools_meta, dict) and "tools" in tools_meta:
            tools = [
                t.get("name") if isinstance(t, dict) else t for t in tools_meta["tools"]
            ]
        elif isinstance(tools_meta, list):
            tools = [t.get("name") if isinstance(t, dict) else t for t in tools_meta]
        else:
            typer.secho(
                f"ERROR: Unexpected response format: {tools_meta}", fg=typer.colors.RED
            )
            return

    payload = {}
    if sample:
        payload = json.loads(sample)

    results = []
    for tname in tools:
        if not tname or not isinstance(tname, str):
            typer.secho(f"SKIPPING invalid tool name: {tname}", fg=typer.colors.YELLOW)
            continue
        try:
            resp = client.call_tool(tname, payload)
        except Exception as e:
            typer.secho(f"ERROR calling {tname}: {e}", fg=typer.colors.RED)
            continue

        # Extract meaningful text content
        content = resp.get("content") or resp.get("result") or resp

        # Convert to string if needed
        if isinstance(content, (dict, list)):
            content = json.dumps(content)
        elif not isinstance(content, str):
            content = str(content)

        tok_count = tokenizer.count(content)
        results.append(
            {
                "tool": tname,
                "tokens": tok_count,
            }
        )

        cost_msg = f"[{tname}] tokens = {tok_count}"
        if cost_per_million is not None:
            cost = (tok_count / 1_000_000) * cost_per_million
            cost_msg += f" | cost = ${cost:.6f}"
        typer.secho(cost_msg, fg=typer.colors.GREEN)

    # pretty-print JSON summary
    typer.echo(json.dumps({"server": server_url, "results": results}, indent=2))


def main():
    app()


if __name__ == "__main__":
    main()
