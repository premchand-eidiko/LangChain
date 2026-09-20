from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from app.database.base import Base
from app.models import Chat, ChatDocument, Document, Message, User
from app.services.chat_service import delete_user_chat


def test_core_tables_are_registered():
    table_names = set(Base.metadata.tables)

    assert table_names == {"users", "chats", "messages", "documents", "chat_documents"}


def test_foreign_keys_enforce_ownership_relationships():
    assert "users.id" in {
        str(foreign_key.target_fullname)
        for foreign_key in Chat.__table__.c.user_id.foreign_keys
    }
    assert "users.id" in {
        str(foreign_key.target_fullname)
        for foreign_key in Document.__table__.c.user_id.foreign_keys
    }
    assert "chats.id" in {
        str(foreign_key.target_fullname)
        for foreign_key in Message.__table__.c.chat_id.foreign_keys
    }


def test_deleting_chat_removes_orphan_documents_but_preserves_shared_files(tmp_path):
    engine = create_engine("sqlite://")
    Base.metadata.create_all(bind=engine)
    db = Session(engine)
    user_id = uuid4()
    first_chat_id = uuid4()
    second_chat_id = uuid4()
    orphan_path = Path(tmp_path) / "orphan.txt"
    shared_path = Path(tmp_path) / "shared.txt"
    orphan_path.write_text("orphan")
    shared_path.write_text("shared")
    db.add(User(id=user_id, email="cleanup@example.com", password_hash="hash"))
    db.add_all([
        Chat(id=first_chat_id, user_id=user_id, title="First"),
        Chat(id=second_chat_id, user_id=user_id, title="Second"),
        Document(id=uuid4(), user_id=user_id, filename="orphan.txt", file_type="txt", storage_path=str(orphan_path)),
        Document(id=uuid4(), user_id=user_id, filename="shared.txt", file_type="txt", storage_path=str(shared_path)),
    ])
    db.commit()
    orphan = db.query(Document).filter_by(filename="orphan.txt").one()
    shared = db.query(Document).filter_by(filename="shared.txt").one()
    db.add_all([
        ChatDocument(chat_id=first_chat_id, document_id=orphan.id),
        ChatDocument(chat_id=first_chat_id, document_id=shared.id),
        ChatDocument(chat_id=second_chat_id, document_id=shared.id),
    ])
    db.commit()

    assert delete_user_chat(db, user_id, first_chat_id)
    assert not orphan_path.exists()
    assert shared_path.exists()
    assert db.get(Document, orphan.id) is None
    assert db.get(Document, shared.id) is not None

    db.close()
    Base.metadata.drop_all(bind=engine)
