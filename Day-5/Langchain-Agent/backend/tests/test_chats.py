import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def register_and_login(client, email):
    password = "strong-password-123"
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post(
        "/auth/login", json={"email": email, "password": password}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_chat_lifecycle_and_message_persistence(client):
    headers = register_and_login(client, "learner@example.com")

    create_response = client.post(
        "/chats", headers=headers, json={"title": "Learning LangChain"}
    )
    assert create_response.status_code == 201
    chat = create_response.json()
    chat_id = chat["id"]
    assert chat["title"] == "Learning LangChain"
    assert chat["messages"] == []

    message_response = client.post(
        "/chats/{}/messages".format(chat_id),
        headers=headers,
        json={"role": "user", "content": "What is RAG?"},
    )
    assert message_response.status_code == 201
    assert message_response.json()["content"] == "What is RAG?"

    detail_response = client.get("/chats/{}".format(chat_id), headers=headers)
    assert detail_response.status_code == 200
    assert len(detail_response.json()["messages"]) == 1

    list_response = client.get("/chats", headers=headers)
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [chat_id]

    delete_response = client.delete("/chats/{}".format(chat_id), headers=headers)
    assert delete_response.status_code == 204
    assert client.get("/chats/{}".format(chat_id), headers=headers).status_code == 404


def test_user_cannot_access_another_users_chat(client):
    owner_headers = register_and_login(client, "owner@example.com")
    other_headers = register_and_login(client, "other@example.com")

    create_response = client.post("/chats", headers=owner_headers, json={})
    chat_id = create_response.json()["id"]

    assert client.get("/chats/{}".format(chat_id), headers=other_headers).status_code == 404
    assert client.post(
        "/chats/{}/messages".format(chat_id),
        headers=other_headers,
        json={"role": "user", "content": "Should be rejected"},
    ).status_code == 404
    assert client.delete("/chats/{}".format(chat_id), headers=other_headers).status_code == 404
    assert client.get("/chats/{}".format(chat_id), headers=owner_headers).status_code == 200
