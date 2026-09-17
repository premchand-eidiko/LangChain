from langchain_text_splitters import RecursiveCharacterTextSplitter

text = """
Company Leave Policy

Employees receive 20 days of annual leave per year.

Employees must apply for leave through the HR portal.

Managers must approve leave requests.

Emergency leave requires manager approval.
"""

splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20
)

chunks = splitter.split_text(text)

print("Number of chunks:", len(chunks))

for i, chunk in enumerate(chunks):
    print(f"\n--- CHUNK {i + 1} ---")
    print(chunk)