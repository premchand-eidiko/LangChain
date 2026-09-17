import os
from pathlib import Path

os.environ.setdefault("USER_AGENT", "langchain-learning-web-loader/1.0")

from langchain_community.document_loaders import WebBaseLoader

base_path = Path(__file__).parent
web_url = "https://www.example.com"
loader = WebBaseLoader(web_path=web_url)

documents = loader.load()
output_path = base_path / "output" / "web.txt"
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", encoding="utf-8") as output_file:
    print("Number of documents:", len(documents), file=output_file)

    for document in documents:
        print("\n--- DOCUMENT ---", file=output_file)
        print("Content:", file=output_file)
        print(document.page_content, file=output_file)

        print("\nMetadata:", file=output_file)
        print(document.metadata, file=output_file)