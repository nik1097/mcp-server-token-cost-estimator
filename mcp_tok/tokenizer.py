from typing import Union

import tiktoken


class Tokenizer:
    def __init__(self, model_name: str = "gpt-4o"):
        # choose encoding by model name; adjust mapping for different models
        # NOTE: pick a close encoding if exact unavailable
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def count(self, text: Union[str, bytes]) -> int:
        if isinstance(text, bytes):
            text = text.decode("utf-8", errors="ignore")
        # Ensure text is a string for encoding
        text_str = str(text) if not isinstance(text, str) else text
        tokens = self.encoding.encode(text_str)
        return len(tokens)
