"""Application workflows used by run.py."""

import shutil

from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    CSV_DIR,
    PDF_DIR,
    RETRIEVAL_K,
    URLS_FILE,
    VECTOR_STORE_DIR,
    load_environment,
)
from src.ingestion.document_loader import load_all_documents
from src.ingestion.text_splitter import split_documents
from src.rag.rag_chain import answer_question, create_llm
from src.retrieval.retriever import create_retriever
from src.vectorstore.chroma_store import create_vector_store, load_vector_store


def ingest() -> None:
    """Load, split, embed, and persist all configured documents."""
    loaded = load_all_documents(PDF_DIR, CSV_DIR, URLS_FILE)
    print(f"Total documents loaded: {len(loaded.documents)}")
    print(f"PDF documents: {loaded.pdf_count}")
    print(f"CSV documents: {loaded.csv_count}")
    print(f"Web documents: {loaded.web_count}")
    if not loaded.documents:
        print("No documents found. Add PDFs, CSVs, or URLs under data/ and try again.")
        return
    chunks = split_documents(loaded.documents, CHUNK_SIZE, CHUNK_OVERLAP)
    print(f"Original documents: {len(loaded.documents)}")
    print(f"Generated chunks: {len(chunks)}")
    if VECTOR_STORE_DIR.exists():
        shutil.rmtree(VECTOR_STORE_DIR)
    create_vector_store(chunks, VECTOR_STORE_DIR)
    print(f"Vector store saved to: {VECTOR_STORE_DIR}")


def chat() -> None:
    """Start the interactive command-line chatbot."""
    load_environment()
    vector_store = load_vector_store(VECTOR_STORE_DIR)
    retriever = create_retriever(vector_store, RETRIEVAL_K)
    llm = create_llm()
    print("\nENTERPRISE DOCUMENT CHATBOT\n")
    print("Type your question. Type 'exit' to quit.\n")
    while True:
        question = input("Question: ").strip()
        if question.lower() == "exit":
            print("Goodbye.")
            return
        if not question:
            print("Please enter a question.")
            continue
        try:
            answer = answer_question(question, retriever, llm)
            print(f"\nAnswer:\n{answer.text}\n\nSources:")
            for document in answer.sources:
                source = document.metadata.get("source", "unknown source")
                page = document.metadata.get("page")
                suffix = f", page {page + 1}" if isinstance(page, int) else ""
                print(f"- {source}{suffix}")
            print()
        except Exception as error:
            print(f"Could not answer the question: {error}")
