import sys

import pysqlite3

sys.modules["sqlite3"] = pysqlite3

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

texts = [
    "Employees receive 20 days of annual leave per year.",
    "Employees must apply for leave through the HR portal.",
    "Python is a programming language used for software development.",
    "The company provides laptops to employees.",
    "Managers must approve employee leave requests."
]

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = Chroma.from_texts(
    texts=texts,
    embedding=embeddings
)

retriever = vector_store.as_retriever(
    search_kwargs={"k": 2}
)

query = "How many vacation days do employees get?"

results = retriever.invoke(query)

print("Query:")
print(query)

print("\nRetrieved documents:")

for i, document in enumerate(results):
    print(f"\n--- Result {i + 1} ---")
    print(document.page_content)