from sqlalchemy import inspect

from app.database.base import Base
from app.models import Chat, Document, Message, User


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
