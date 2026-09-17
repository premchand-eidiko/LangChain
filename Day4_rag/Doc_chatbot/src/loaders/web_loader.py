"""Web page loading helpers."""

import os

os.environ.setdefault("USER_AGENT", "enterprise-document-chatbot/1.0")

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document


def load_web_page(url: str) -> list[Document]:
    """Load one web page and return its LangChain documents."""
    return WebBaseLoader(web_paths=[url]).load()
