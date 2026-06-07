# -*- coding: utf-8 -*-
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.requirement_db import CambioEstadoDB, RequerimientooDB  # noqa: F401
from app.models.user_db import UsuarioDB  # noqa: F401

SQLALCHEMY_TEST_URL = "sqlite://"

_ADMIN_DATA = {
    "email": "admin@test.com",
    "password": "admin123",
    "nombre": "Admin Test",
    "rol": "administrador",
}

_FUNCIONARIO_DATA = {
    "email": "funcionario@test.com",
    "password": "func123",
    "nombre": "Funcionario Test",
    "rol": "funcionario",
}


@pytest.fixture
def client():
    engine = create_engine(
        SQLALCHEMY_TEST_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def _get_token(client: TestClient, user_data: dict) -> str:
    client.post("/auth/registro", json=user_data)
    resp = client.post(
        "/auth/token",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    return resp.json()["access_token"]


@pytest.fixture
def admin_token(client: TestClient) -> str:
    return _get_token(client, _ADMIN_DATA)


@pytest.fixture
def funcionario_token(client: TestClient) -> str:
    return _get_token(client, _FUNCIONARIO_DATA)
