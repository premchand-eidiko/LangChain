from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)

prompt = ChatPromptTemplate.from_template(
    "In LangChain, explain LangChain Expression Language (LCEL) to a beginner. "
    "Focus on this topic: {topic}"
)

parser = StrOutputParser()
chain = prompt | model | parser

result = chain.invoke({"topic": "the prompt-model pipeline"})
print("Model output:")
print(result)
print("Model output type:", type(result))
print("Final output type:", type(result))

formatted_prompt = prompt.invoke({"topic": "the prompt-model pipeline"})

print("Prompt output:")
print(formatted_prompt)
print("Prompt output type:", type(formatted_prompt))