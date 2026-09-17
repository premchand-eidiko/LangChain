"""Command-line entry point for the Enterprise Document Chatbot."""

import sys

from src.main import chat, ingest


def main() -> None:
    command = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    if command == "ingest":
        ingest()
    elif command == "chat":
        chat()
    elif command == "rebuild":
        ingest()
    else:
        print("Usage: python run.py [ingest|chat|rebuild]")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
