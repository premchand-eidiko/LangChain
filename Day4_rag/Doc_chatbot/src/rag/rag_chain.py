"""Small, explicit RAG workflow with source reporting."""

import os
from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_groq import ChatGroq

from src.config import GROQ_MODEL, load_environment
from src.rag.prompt import RAG_PROMPT


@dataclass
class Answer:
    """Generated answer and the documents used to produce it."""

    text: str
    sources: list[Document]


def format_context(documents: list[Document]) -> str:
    """Format content and available metadata for the prompt."""
    blocks = []
    for index, document in enumerate(documents, start=1):
        metadata = document.metadata
        source = metadata.get("source", "unknown source")
        page = metadata.get("page")
        location = f"{source}, page {page + 1}" if isinstance(page, int) else str(source)
        author = metadata.get("author")
        author_line = f"\nAuthor: {author}" if author else ""
        blocks.append(
            f"DOCUMENT {index}\nSource: {location}{author_line}\n\n"
            f"{document.page_content}"
        )
    return "\n\n".join(blocks)


def create_llm() -> ChatGroq:
    """Create the configured Groq chat model after loading .env."""
    load_environment()
    if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "your_api_key_here":
        raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file before chat.")
    return ChatGroq(model=GROQ_MODEL, temperature=0)


def answer_question(question: str, retriever, llm) -> Answer:
    """Retrieve context, invoke the prompt and LLM, and return sources."""
    documents = retriever.invoke(question)
    messages = RAG_PROMPT.invoke(
        {"context": format_context(documents), "question": question}
    )
    response = llm.invoke(messages)
    text = response.content if hasattr(response, "content") else str(response)
    return Answer(text=text, sources=documents)
