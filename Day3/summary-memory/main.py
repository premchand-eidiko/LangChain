from dataclasses import dataclass


@dataclass
class Turn:
    role: str
    content: str


class SummaryMemory:
    """Keep a summary for old turns and a small window of recent turns."""

    def __init__(self, max_recent_turns: int = 2) -> None:
        if max_recent_turns < 1:
            raise ValueError("max_recent_turns must be at least 1")
        self.max_recent_turns = max_recent_turns
        self.summary = ""
        self.recent_turns: list[Turn] = []

    def add(self, role: str, content: str) -> None:
        self.recent_turns.append(Turn(role, content))
        while len(self.recent_turns) > self.max_recent_turns:
            oldest = self.recent_turns.pop(0)
            self.summary = self.summarize(oldest)

    def summarize(self, turn: Turn) -> str:
        sentence = f"{turn.role} said: {turn.content}"
        return f"{self.summary} {sentence}".strip()

    def load_context(self) -> str:
        recent = "\n".join(
            f"{turn.role}: {turn.content}" for turn in self.recent_turns
        )
        sections = [section for section in (
            f"Summary: {self.summary}" if self.summary else "",
            recent,
        ) if section]
        return "\n".join(sections)


if __name__ == "__main__":
    memory = SummaryMemory(max_recent_turns=2)
    print("Enter conversation turns. Leave the role empty to finish.")
    while True:
        role = input("Role (user/assistant): ").strip()
        if not role:
            break
        content = input("Message: ").strip()
        if content:
            memory.add(role, content)

    print(memory.load_context())
