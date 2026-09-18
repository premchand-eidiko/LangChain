import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.database.base import Base
from app.database.session import get_db
from app.main import app


@pytest.fixture
def client(tmp_path):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    settings = get_settings()
    original_upload_dir = settings.upload_dir
    settings.upload_dir = str(tmp_path)

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client, tmp_path
    app.dependency_overrides.clear()
    settings.upload_dir = original_upload_dir
    Base.metadata.drop_all(bind=engine)


def register_and_login(client, email):
    password = "strong-password-123"
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post(
        "/auth/login", json={"email": email, "password": password}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_valid_upload_list_and_delete(client):
    test_client, upload_dir = client
    headers = register_and_login(test_client, "learner@example.com")

    response = test_client.post(
        "/documents/upload",
        headers=headers,
        files={"upload": ("notes.txt", b"RAG notes", "text/plain")},
    )
    assert response.status_code == 201
    document = response.json()
    assert document["filename"] == "notes.txt"
    assert document["file_type"] == "txt"
    stored_files = list(upload_dir.iterdir())
    assert len(stored_files) == 1
    assert stored_files[0].read_bytes() == b"RAG notes"

    list_response = test_client.get("/documents", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == document["id"]

    delete_response = test_client.delete(
        "/documents/{}".format(document["id"]), headers=headers
    )
    assert delete_response.status_code == 204
    assert list(upload_dir.iterdir()) == []


def test_invalid_document_is_rejected(client):
    test_client, _ = client
    headers = register_and_login(test_client, "learner@example.com")

    unsupported = test_client.post(
        "/documents/upload",
        headers=headers,
        files={"upload": ("script.exe", b"not allowed", "application/octet-stream")},
    )
    assert unsupported.status_code == 400

    empty = test_client.post(
        "/documents/upload",
        headers=headers,
        files={"upload": ("empty.txt", b"", "text/plain")},
    )
    assert empty.status_code == 400


def test_user_cannot_access_another_users_document(client):
    test_client, upload_dir = client
    owner_headers = register_and_login(test_client, "owner@example.com")
    other_headers = register_and_login(test_client, "other@example.com")

    upload_response = test_client.post(
        "/documents/upload",
        headers=owner_headers,
        files={"upload": ("private.csv", b"private,data", "text/csv")},
    )
    document_id = upload_response.json()["id"]

    other_documents = test_client.get("/documents", headers=other_headers)
    assert other_documents.status_code == 200
    assert other_documents.json() == []
    assert test_client.delete(
        "/documents/{}".format(document_id), headers=other_headers
    ).status_code == 404
    assert len(list(upload_dir.iterdir())) == 1
