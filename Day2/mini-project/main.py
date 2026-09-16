from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnableSequence,
)
from langchain_groq import ChatGroq
from dotenv import load_dotenv

import os
import sys

# -------------------- Output --------------------

output_file = open("output.txt", "w", encoding="utf-8", buffering=1)
sys.stdout = output_file
sys.stderr = output_file


# -------------------- Environment --------------------

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError(
        "GROQ_API_KEY is not set. Add it to .env before running this program."
    )


# -------------------- Model --------------------

model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=600,
    reasoning_format="hidden",
)


# -------------------- Shared Transformation --------------------

def extract_content(message):
    return message.content


content_extractor = RunnableLambda(extract_content)


# -------------------- Step 1: Explanation --------------------

explanation_prompt = PromptTemplate.from_template(
    "Explain {topic} in a concise, beginner-friendly way."
)

explanation_chain = RunnableSequence(explanation_prompt, model, content_extractor)


# -------------------- Step 2: Parallel Tasks --------------------

summary_prompt = PromptTemplate.from_template(
    "Summarize {topic} in exactly three beginner-friendly bullet points."
)

example_prompt = PromptTemplate.from_template(
    "Give one simple Python code example for {topic}. Explain the code briefly."
)

interview_prompt = PromptTemplate.from_template(
    "Create one beginner-friendly interview question about {topic}, followed by its answer."
)

summary_chain = RunnableSequence(summary_prompt, model, content_extractor)
example_chain = RunnableSequence(example_prompt, model, content_extractor)
interview_chain = RunnableSequence(interview_prompt, model, content_extractor)

parallel_chain = RunnableParallel(
    summary=summary_chain,
    python_example=example_chain,
    interview=interview_chain,
)


# -------------------- Step 3: Complete Workflow --------------------

def run_workflow(topic):
    explanation = explanation_chain.invoke({"topic": topic})

    parallel_results = parallel_chain.invoke({"topic": topic})

    return {
        "explanation": explanation,
        **parallel_results,
    }


# -------------------- Step 4: Application --------------------

print("Enter a topic: ", end="", file=sys.__stdout__, flush=True)
topic = input().strip()

if not topic:
    raise ValueError("Topic cannot be empty.")

result = run_workflow(topic)

print("========== EXPLANATION ==========")
print(result["explanation"])
print()
print("========== SUMMARY ==========")
print(result["summary"])
print()
print("========== PYTHON EXAMPLE ==========")
print(result["python_example"])
print()
print("========== INTERVIEW QUESTION ==========")
print(result["interview"])

output_file.close()