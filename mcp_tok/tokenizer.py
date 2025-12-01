from typing import Union

import tiktoken


class Tokenizer:
    """Tokenizer using tiktoken with cl100k_base encoding."""

    def __init__(self):
        self.encoding = tiktoken.get_encoding("o200k_base")

    def count(self, text: Union[str, bytes]) -> int:
        if isinstance(text, bytes):
            text = text.decode("utf-8", errors="ignore")
        text_str = str(text) if not isinstance(text, str) else text
        tokens = self.encoding.encode(text_str)
        return len(tokens)
