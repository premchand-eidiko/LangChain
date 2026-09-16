from langchain_core.runnables import RunnableLambda, RunnableParallel


def summary(values: dict[str, str]) -> str:
    return f"Short summary of {values['topic']}"


def example(values: dict[str, str]) -> str:
    return f"Simple example of {values['topic']}"


def interview_question(values: dict[str, str]) -> str:
    return f"Interview question about {values['topic']}"


parallel = RunnableParallel(
    summary=RunnableLambda(summary),
    example=RunnableLambda(example),
    interview=RunnableLambda(interview_question),
)


if __name__ == "__main__":
    result = parallel.invoke({"topic": "RunnableParallel"})
    for name, value in result.items():
        print(f"{name}: {value}")
