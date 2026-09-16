from langchain_core.runnables import RunnableLambda, RunnableSequence


def clean_topic(values: dict[str, str]) -> str:
    return values["topic"].strip().lower()


def create_prompt(topic: str) -> str:
    return f"Explain {topic} to a beginner."


def add_label(prompt: str) -> str:
    return f"FINAL PROMPT: {prompt}"


chain = RunnableSequence(
    RunnableLambda(clean_topic),
    RunnableLambda(create_prompt),
    RunnableLambda(add_label),
)


if __name__ == "__main__":
    result = chain.invoke({"topic": "  RunnableSequence  "})
    print(result)
