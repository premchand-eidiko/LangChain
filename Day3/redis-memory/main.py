from __future__ import annotations

import json


class RedisConversationMemory:
    """Store conversation turns as JSON under one key per session."""

    def __init__(self, client) -> None:
        self.client = client

    @staticmethod
    def _key(session_id: str) -> str:
        return f"conversation:{session_id}"

    def load(self, session_id: str) -> list[dict[str, str]]:
        value = self.client.get(self._key(session_id))
        return json.loads(value) if value else []

    def save(self, session_id: str, turns: list[dict[str, str]]) -> None:
        self.client.set(self._key(session_id), json.dumps(turns))


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def get(self, key: str):
        return self.values.get(key)

    def set(self, key: str, value: str) -> None:
        self.values[key] = value


if __name__ == "__main__":
    memory = RedisConversationMemory(FakeRedis())
    session_id = input("Session ID: ").strip()
    turns = []
    print("Enter turns. Leave the role empty to finish.")
    while session_id:
        role = input("Role (user/assistant): ").strip()
        if not role:
            break
        content = input("Message: ").strip()
        if content:
            turns.append({"role": role, "content": content})

    if session_id:
        memory.save(session_id, turns)
        print(memory.load(session_id))
