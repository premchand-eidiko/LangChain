from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models import Document, User
from app.rag.splitter import split_documents
from app.rag.vectorstore import UserVectorStore
from app.tools.document_tool import DocumentSearchInput, build_document_search_tool
from langchain_core.documents import Document as LangChainDocument


def test_document_tool_searches_only_owned_document(tmp_path):
    engine = create_engine("sqlite://")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    db = session_factory()

    owner_id = uuid4()
    other_user_id = uuid4()
    document_id = uuid4()
    other_document_id = uuid4()
    db.add_all(
        [
            User(id=owner_id, email="owner@example.com", password_hash="hash"),
            User(id=other_user_id, email="other@example.com", password_hash="hash"),
            Document(
                id=document_id,
                user_id=owner_id,
                filename="policy.txt",
                file_type="txt",
                storage_path=str(Path(tmp_path) / "policy.txt"),
            ),
            Document(
                id=other_document_id,
                user_id=other_user_id,
                filename="other.txt",
                file_type="txt",
                storage_path=str(Path(tmp_path) / "other.txt"),
            ),
        ]
    )
    db.commit()

    store = UserVectorStore()
    store.add_chunks(
        owner_id,
        split_documents(
            [LangChainDocument(page_content="Annual leave is twenty days.")],
            owner_id,
            document_id,
        ),
    )
    tool = build_document_search_tool(db, owner_id, store)

    result = tool.invoke(
        {"document_id": str(document_id), "query": "How many leave days?"}
    )
    assert "twenty days" in result

    unauthorized_result = tool.invoke(
        {"document_id": str(other_document_id), "query": "private information"}
    )
    assert unauthorized_result == "The requested document was not found."

    db.close()
    Base.metadata.drop_all(bind=engine)


def test_document_tool_has_structured_input():
    tool = build_document_search_tool(None, uuid4())
    assert tool.args_schema is DocumentSearchInput
    assert set(tool.args_schema.model_fields) == {"document_id", "filename", "query"}