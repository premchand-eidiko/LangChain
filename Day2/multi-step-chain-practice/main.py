from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnableSequence


def prepare(values: dict[str, str]) -> str:
    return values["topic"].strip()


def explain(topic: str) -> str:
    return f"Explanation of {topic}"


def format_answer(answer: str) -> str:
    return answer.upper()


def summary(values: dict[str, str]) -> str:
    return f"Summary of {values['topic']}"


def example(values: dict[str, str]) -> str:
    return f"Example for {values['topic']}"


explanation_chain = RunnableSequence(
    RunnableLambda(prepare),
    RunnableLambda(explain),
    RunnableLambda(format_answer),
)
parallel_chain = RunnableParallel(
    summary=RunnableLambda(summary),
    example=RunnableLambda(example),
)


def run_workflow(topic: str) -> dict[str, str]:
    values = {"topic": topic}
    return {
        "explanation": explanation_chain.invoke(values),
        **parallel_chain.invoke(values),
    }


if __name__ == "__main__":
    for name, value in run_workflow(" Prompt Templates ").items():
        print(f"{name}: {value}")
