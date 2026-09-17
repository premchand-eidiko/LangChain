from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

text = "Employees receive 20 days of annual leave."

vector = embeddings.embed_query(text)

print("Vector:")
print(vector)

print("\nVector length:")
print(len(vector))