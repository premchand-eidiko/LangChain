from __future__ import annotations

from collections import defaultdict


class EntityMemory:
    """Store the latest known facts for each named entity."""

    def __init__(self) -> None:
        self.facts: dict[str, dict[str, str]] = defaultdict(dict)

    def remember(self, entity: str, attribute: str, value: str) -> None:
        self.facts[entity][attribute] = value

    def get(self, entity: str) -> dict[str, str]:
        return dict(self.facts.get(entity, {}))

    def context_for(self, entity: str) -> str:
        facts = self.get(entity)
        if not facts:
            return f"No facts known about {entity}."
        details = ", ".join(f"{key}={value}" for key, value in facts.items())
        return f"Known facts about {entity}: {details}"


if __name__ == "__main__":
    memory = EntityMemory()
    print("Enter entity facts. Leave the entity empty to finish.")
    while True:
        entity = input("Entity: ").strip()
        if not entity:
            break
        attribute = input("Attribute: ").strip()
        value = input("Value: ").strip()
        if attribute and value:
            memory.remember(entity, attribute, value)

    for entity in memory.facts:
        print(memory.context_for(entity))
