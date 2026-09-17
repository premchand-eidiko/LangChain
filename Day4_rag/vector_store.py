import sys

import pysqlite3

sys.modules["sqlite3"] = pysqlite3
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Create embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Our documents
texts = [
    "Python is a programming language.",
    "FastAPI is a Python web framework.",
    "SQL is used to work with databases.",
    "LangChain is used to build applications with language models."
]

# Create vector store
vector_store = Chroma.from_texts(
    texts=texts,
    embedding=embeddings,
    persist_directory="./chroma_db",
    collection_name="my_documents"
)

print("Vector store created successfully!")