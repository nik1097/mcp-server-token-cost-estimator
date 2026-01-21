import json
from typing import Any, Dict, List, Optional, Union

import anthropic
import tiktoken


class Tokenizer:
    """Tokenizer supporting both OpenAI (tiktoken) and Claude (Anthropic) token counting."""

    def __init__(
        self,
        provider: str = "openai",
        anthropic_config: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize tokenizer for specified provider.

        Args:
            provider: Either "openai" or "claude"
            anthropic_config: Dict with "base_url", "api_key", "model" for Claude
        """
        self.provider = provider.lower()

        if self.provider == "openai":
            self.encoding = tiktoken.get_encoding("o200k_base")
            self.anthropic_client = None
            self.model = None
        elif self.provider == "claude":
            if not anthropic_config:
                raise ValueError("anthropic_config required for Claude provider")

            self.anthropic_client = anthropic.Anthropic(
                base_url=anthropic_config.get("base_url"),
                api_key=anthropic_config.get("api_key"),
                default_headers={"anthropic-version": "2023-06-01"},
            )
            self.model = anthropic_config.get("model", "claude-sonnet-4-5")
            self.encoding = None
        else:
            raise ValueError(
                f"Unknown provider: {provider}. Must be 'openai' or 'claude'"
            )

    def count(self, text: Union[str, bytes]) -> int:
        """Count tokens in text using the configured provider."""
        if isinstance(text, bytes):
            text = text.decode("utf-8", errors="ignore")
        text_str = str(text) if not isinstance(text, str) else text

        if self.provider == "openai":
            tokens = self.encoding.encode(text_str)
            return len(tokens)
        else:  # claude
            # Use Claude's count_tokens API
            response = self.anthropic_client.messages.count_tokens(
                model=self.model, messages=[{"role": "user", "content": text_str}]
            )
            return response.input_tokens

    def count_with_tools(self, message: str, tools: List[Dict[str, Any]]) -> int:
        """Count tokens including tool definitions (Claude-specific feature)."""
        if self.provider == "openai":
            # For OpenAI, approximate by counting message + tool definitions
            combined = json.dumps({"message": message, "tools": tools})
            return self.count(combined)
        else:  # claude
            response = self.anthropic_client.messages.count_tokens(
                model=self.model,
                tools=tools,
                messages=[{"role": "user", "content": message}],
            )
            return response.input_tokens
