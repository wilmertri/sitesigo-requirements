# -*- coding: utf-8 -*-
from fastapi.testclient import TestClient

_ADMIN = {
    "email": "admin@test.com",
    "password": "admin123",
    "nombre": "Admin Test",
    "rol": "administrador",
}


def test_registro_usuario_nuevo_devuelve_201(client: TestClient):
    response = client.post("/auth/registro", json=_ADMIN)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "admin@test.com"
    assert data["rol"] == "administrador"
    assert "hashed_password" not in data


def test_registro_email_duplicado_devuelve_400(client: TestClient):
    client.post("/auth/registro", json=_ADMIN)
    response = client.post("/auth/registro", json=_ADMIN)
    assert response.status_code == 400


def test_login_credenciales_correctas_devuelve_token(client: TestClient):
    client.post("/auth/registro", json=_ADMIN)
    response = client.post(
        "/auth/token",
        data={"username": "admin@test.com", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_credenciales_incorrectas_devuelve_401(client: TestClient):
    client.post("/auth/registro", json=_ADMIN)
    response = client.post(
        "/auth/token",
        data={"username": "admin@test.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_me_con_token_valido_devuelve_usuario(client: TestClient):
    client.post("/auth/registro", json=_ADMIN)
    login = client.post(
        "/auth/token",
        data={"username": "admin@test.com", "password": "admin123"},
    )
    token = login.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "admin@test.com"
