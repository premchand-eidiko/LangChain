from langchain_core.runnables import RunnableBranch, RunnableLambda


def is_summary(values: dict[str, str]) -> bool:
    return "summary" in values["request"].lower()


def is_explanation(values: dict[str, str]) -> bool:
    return "explain" in values["request"].lower()


def make_summary(values: dict[str, str]) -> str:
    return f"Summary chain selected for: {values['request']}"


def make_explanation(values: dict[str, str]) -> str:
    return f"Explanation chain selected for: {values['request']}"


def make_general_answer(values: dict[str, str]) -> str:
    return f"General chain selected for: {values['request']}"


chain = RunnableBranch(
    (is_summary, RunnableLambda(make_summary)),
    (is_explanation, RunnableLambda(make_explanation)),
    RunnableLambda(make_general_answer),
)


if __name__ == "__main__":
    for request in [
        "Give me a summary of prompts",
        "Explain RunnableBranch",
        "What is a chain?",
    ]:
        print(chain.invoke({"request": request}))
