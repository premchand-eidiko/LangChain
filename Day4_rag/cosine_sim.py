from langchain_huggingface import HuggingFaceEmbeddings
from numpy import dot
from numpy.linalg import norm

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

texts = [
    "Employees receive 20 days of annual leave.",
    "How many vacation days do employees get?",
    "The company sells laptops and mobile phones."
]

vectors = embeddings.embed_documents(texts)

similarity_1_2 = dot(vectors[0], vectors[1]) / (
    norm(vectors[0]) * norm(vectors[1])
)

similarity_1_3 = dot(vectors[0], vectors[2]) / (
    norm(vectors[0]) * norm(vectors[2])
)

print("Similarity between text 1 and text 2:", similarity_1_2)
print("Similarity between text 1 and text 3:", similarity_1_3)