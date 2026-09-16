from __future__ import annotations

import json
from pathlib import Path


class LongTermMemory:
    """Persist user facts in a small human-readable JSON document."""

    def __init__(self, path: str | Path = "memory.json") -> None:
        self.path = Path(path)
        self.facts: dict[str, dict[str, str]] = self._load()

    def _load(self) -> dict[str, dict[str, str]]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def remember(self, user_id: str, key: str, value: str) -> None:
        self.facts.setdefault(user_id, {})[key] = value
        self.path.write_text(
            json.dumps(self.facts, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def get(self, user_id: str) -> dict[str, str]:
        return dict(self.facts.get(user_id, {}))


if __name__ == "__main__":
    memory = LongTermMemory()
    user_id = input("User ID: ").strip()
    key = input("Fact name: ").strip()
    value = input("Fact value: ").strip()
    if user_id and key and value:
        memory.remember(user_id, key, value)
        print(memory.get(user_id))
