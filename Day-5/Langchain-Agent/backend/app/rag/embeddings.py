from __future__ import annotations

import hashlib
import math
from typing import List

from langchain_core.embeddings import Embeddings


class DevelopmentEmbeddings(Embeddings):
    """Deterministic local embeddings for development and tests.

    Production can replace this class with an API-backed embedding model without
    changing the splitter, vector store, or retriever contracts.
    """

    dimensions = 64

    def _embed(self, text: str) -> List[float]:
        values = [0.0] * self.dimensions
        tokens = text.lower().split()
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:2], "big") % self.dimensions
            values[index] += 1.0 if digest[2] % 2 else -1.0
        magnitude = math.sqrt(sum(value * value for value in values))
        if magnitude == 0:
            return values
        return [value / magnitude for value in values]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)
