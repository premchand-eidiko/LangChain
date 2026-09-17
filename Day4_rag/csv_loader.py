from pathlib import Path

from langchain_community.document_loaders import CSVLoader

base_path = Path(__file__).parent
csv_path = base_path / "docs" / "sample.csv"
loader = CSVLoader(file_path=str(csv_path))

documents = loader.load()
output_path = base_path / "output" / "csv.txt"
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", encoding="utf-8") as output_file:
    print("Number of documents:", len(documents), file=output_file)

    for document in documents:
        print("\n--- DOCUMENT ---", file=output_file)
        print("Content:", file=output_file)
        print(document.page_content, file=output_file)

        print("\nMetadata:", file=output_file)
        print(document.metadata, file=output_file)