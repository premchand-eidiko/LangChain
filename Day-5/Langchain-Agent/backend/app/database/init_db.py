from app.database.base import Base
from app.database.connection import engine
from app.models import Chat, ChatDocument, Document, Message, User


def create_tables() -> None:
    # Importing the models above registers every table with Base.metadata.
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
