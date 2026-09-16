from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

model = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0,
    max_tokens=500,
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful teacher. Answer in exactly 3 short bullet points."),
        ("human", "{question}"),
    ]
)

question = input("What would you like to ask? ")

print("You asked:", question)

parser = StrOutputParser()
chain = prompt | model | parser

answer = chain.invoke({"question": question})

print("\nAssistant:")
print(answer)