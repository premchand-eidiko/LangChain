from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    FewShotPromptTemplate,
    PromptTemplate,
)


examples = [
    {"question": "What is Python?", "answer": "Python is a programming language."},
    {"question": "What is Redis?", "answer": "Redis is an in-memory data store."},
]
example_prompt = PromptTemplate.from_template(
    "Question: {question}\nAnswer: {answer}"
)

text_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="Answer in the same short style as the examples.",
    suffix="Question: {question}\nAnswer:",
    input_variables=["question"],
)

chat_example_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=ChatPromptTemplate.from_messages([
        ("human", "{question}"),
        ("ai", "{answer}"),
    ]),
    examples=examples,
)
chat_prompt = chat_example_prompt


if __name__ == "__main__":
    print("FewShotPromptTemplate output:\n")
    print(text_prompt.invoke({"question": "What is LangChain?"}).text)

    print("\nFew-shot chat examples:\n")
    for message in chat_prompt.invoke({}).messages:
        print(f"{message.type}: {message.content}")
