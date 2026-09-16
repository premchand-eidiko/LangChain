from langchain_core.prompts import ChatPromptTemplate, PromptTemplate


text_prompt = PromptTemplate.from_template(
    "Explain {topic} to a {audience} in three short sentences."
)

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a patient programming teacher."),
    ("human", "Explain {topic} to a {audience} in three short sentences."),
])


if __name__ == "__main__":
    values = {"topic": "RunnableSequence", "audience": "beginner"}

    print("PromptTemplate output:")
    print(text_prompt.invoke(values).text)

    print("\nChatPromptTemplate output:")
    for message in chat_prompt.invoke(values).messages:
        print(f"{message.type}: {message.content}")
