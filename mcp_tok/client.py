import requests
import json
from typing import Any, Dict, Optional


class MCPClient:
    """
    Minimal HTTP MCP client to fetch tools and call them directly.
    Uses JSON-RPC 2.0 protocol over SSE (Server-Sent Events) for MCP servers.

    Supports optional Bearer token auth.
    """

    def __init__(
        self, base_url: str, token: Optional[str] = None, timeout: float = 30.0
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.request_id = 0

        # Build a session with auth headers if token is provided
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "User-Agent": "mcp-cost-estimator/0.1",
            }
        )
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def _parse_sse_response(self, response: requests.Response) -> Dict[str, Any]:
        """Parse Server-Sent Events response and extract JSON-RPC result."""
        result = None

        # Read the response line by line
        for line in response.iter_lines(decode_unicode=True):
            if not line or line.startswith(":"):
                # Skip empty lines and comments
                continue

            # SSE format: "data: <json>"
            if line.startswith("data: "):
                data_str = line[6:]  # Remove "data: " prefix
                try:
                    data = json.loads(data_str)

                    # Check if this is a JSON-RPC response (not a ping)
                    if "jsonrpc" in data and data.get("id") == self.request_id:
                        if "error" in data:
                            raise Exception(f"MCP Error: {data['error']}")
                        result = data.get("result", {})
                        break
                except json.JSONDecodeError:
                    # Skip malformed JSON
                    continue

        if result is None:
            raise Exception("No valid JSON-RPC response received from server")

        return result

    def _make_jsonrpc_request(
        self, method: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make a JSON-RPC 2.0 request to the MCP server over SSE."""
        self.request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self.request_id,
        }

        # POST to the base URL with SSE streaming
        response = self.session.post(
            self.base_url,
            json=payload,
            timeout=self.timeout,
            stream=True,  # Enable streaming for SSE
        )
        response.raise_for_status()

        # Parse the SSE response
        return self._parse_sse_response(response)

    def get_tools(self) -> Dict[str, Any]:
        """List all available tools from the MCP server."""
        return self._make_jsonrpc_request("tools/list")

    def call_tool(
        self, tool_name: str, payload: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Call a specific tool on the MCP server."""
        params = {"name": tool_name, "arguments": payload or {}}
        return self._make_jsonrpc_request("tools/call", params)
