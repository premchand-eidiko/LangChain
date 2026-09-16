# Buffer Memory

Buffer memory stores every conversation turn in order. It is the easiest memory
type to understand and gives the model the complete history, but the history
grows until it becomes too large or expensive to send.

## Run

```bash
python main.py
```

Enter user messages when prompted and type `exit` to finish. The demo creates an
assistant response after every user message and stores both turns in memory.

## Practice

Try this sequence:

```text
You: hi im Prem
You: my name is Prem
You: what is my name?
```

The responses come from simple Python rules, not an LLM. This keeps the memory
behavior visible while learning. The response can answer both questions because
the earlier turns are still in the buffer. Memory starts empty each time because
it exists only while this process is running; nothing is summarized or discarded
during one run.
