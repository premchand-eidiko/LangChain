from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass
class Turn:
    role: str
    content: str


class BufferMemory:
    """Keep every user and assistant message in conversation order."""

    def __init__(self) -> None:
        self.turns: list[Turn] = []

    def add(self, role: str, content: str) -> None:
        self.turns.append(Turn(role=role, content=content))

    def as_text(self) -> str:
        return "\n".join(f"{turn.role}: {turn.content}" for turn in self.turns)

    def clear(self) -> None:
        self.turns.clear()


def extract_name(message: str) -> str | None:
    for pattern in (
        r"\bmy name is ([A-Za-z][A-Za-z -]*)",
        r"\b(?:i am|i'm|im) ([A-Za-z][A-Za-z -]*)",
    ):
        match = re.search(pattern, message, re.I)
        if match:
            return match.group(1).strip().rstrip(".!?")
    return None


def find_name(memory: BufferMemory) -> str | None:
    for turn in memory.turns:
        name = extract_name(turn.content)
        if name:
            return name
    return None


def find_favorite_subject(memory: BufferMemory) -> str | None:
    for turn in memory.turns:
        match = re.search(
            r"\bmy fav(?:orite)? subject is ([A-Za-z][A-Za-z -]*)",
            turn.content,
            re.I,
        )
        if match:
            return match.group(1).strip().rstrip(".!?,")
    return None


def reply(memory: BufferMemory, user_message: str) -> str:
    memory.add("user", user_message)
    normalized_message = user_message.lower()

    if "what is my name" in normalized_message or "whats my name" in normalized_message:
        name = find_name(memory)
        response = f"Your name is {name}." if name else "I do not know your name yet."
    elif "what is my fav subject" in normalized_message or "what is my favorite subject" in normalized_message:
        subject = find_favorite_subject(memory)
        response = (
            f"Your favorite subject is {subject}."
            if subject
            else "I do not know your favorite subject yet."
        )
    else:
        new_name = extract_name(user_message)
        new_subject = find_favorite_subject(memory)
        if new_name:
            response = f"Nice to meet you, {new_name}."
            if new_subject:
                response += f" I will remember that your favorite subject is {new_subject}."
        else:
            response = "I do not know that yet."

    memory.add("assistant", response)
    return response


if __name__ == "__main__":
    memory = BufferMemory()
    print("Start chatting. Type 'exit' to finish.")
    while True:
        user_message = input("You: ").strip()
        if user_message.lower() in {"exit", "quit"}:
            break
        if not user_message:
            continue
        print(f"Assistant: {reply(memory, user_message)}")

    print("Complete conversation:")
    print(memory.as_text())
    print(f"\nStored turns: {len(memory.turns)}")
