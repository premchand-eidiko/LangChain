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


def test_registration_and_duplicate_registration(client):
    payload = {"email": "Learner@Example.com", "password": "strong-password-123"}

    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    assert response.json()["email"] == "learner@example.com"
    assert "password" not in response.json()
    assert "password_hash" not in response.json()

    duplicate_response = client.post("/auth/register", json=payload)
    assert duplicate_response.status_code == 409


def test_invalid_login_is_rejected(client):
    client.post(
        "/auth/register",
        json={"email": "learner@example.com", "password": "strong-password-123"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "learner@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_valid_login_and_protected_endpoint(client):
    client.post(
        "/auth/register",
        json={"email": "learner@example.com", "password": "strong-password-123"},
    )

    login_response = client.post(
        "/auth/login",
        json={"email": "learner@example.com", "password": "strong-password-123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert login_response.json()["token_type"] == "bearer"

    unauthorized_response = client.get("/auth/me")
    assert unauthorized_response.status_code == 401

    me_response = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "learner@example.com"
