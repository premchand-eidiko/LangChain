from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader

pdf_path = Path(__file__).parent / "docs" / "sample.pdf"
loader = PyPDFLoader(str(pdf_path))

documents = loader.load()
output_path = Path(__file__).parent / "output" / "pdf.txt"
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", encoding="utf-8") as output_file:
    print("Number of documents:", len(documents), file=output_file)

    for document in documents:
        print("\n--- DOCUMENT ---", file=output_file)
        print("Content:", file=output_file)
        print(document.page_content, file=output_file)

        print("\nMetadata:", file=output_file)
        print(document.metadata, file=output_file)