# -*- coding: utf-8 -*-
from fastapi.testclient import TestClient

_BODY_VALIDO = {
    "titulo": "Modulo de login",
    "descripcion": "Autenticacion con email y password",
    "tipo": "Nueva funcionalidad",
    "prioridad": "Alta",
}


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_crear_requerimiento_valido_devuelve_201(client: TestClient, funcionario_token: str):
    response = client.post("/requerimientos/", json=_BODY_VALIDO, headers=_auth(funcionario_token))
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["titulo"] == "Modulo de login"
    assert data["estado"] == "Nuevo"


def test_crear_requerimiento_sin_titulo_devuelve_422(client: TestClient, funcionario_token: str):
    body = {k: v for k, v in _BODY_VALIDO.items() if k != "titulo"}
    response = client.post("/requerimientos/", json=body, headers=_auth(funcionario_token))
    assert response.status_code == 422


def test_listar_requerimientos_devuelve_200(client: TestClient, admin_token: str):
    response = client.get("/requerimientos/", headers=_auth(admin_token))
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_cambiar_estado_como_admin_devuelve_200(client: TestClient, admin_token: str, funcionario_token: str):
    create_resp = client.post("/requerimientos/", json=_BODY_VALIDO, headers=_auth(funcionario_token))
    req_id = create_resp.json()["id"]

    response = client.patch(
        f"/requerimientos/{req_id}/estado",
        json={"nuevo_estado": "En analisis"},
        headers=_auth(admin_token),
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "En analisis"


def test_cambiar_estado_como_funcionario_devuelve_403(client: TestClient, funcionario_token: str):
    create_resp = client.post("/requerimientos/", json=_BODY_VALIDO, headers=_auth(funcionario_token))
    req_id = create_resp.json()["id"]

    response = client.patch(
        f"/requerimientos/{req_id}/estado",
        json={"nuevo_estado": "En analisis"},
        headers=_auth(funcionario_token),
    )
    assert response.status_code == 403


def test_obtener_detalle_requerimiento_existente(
    client: TestClient, admin_token: str, funcionario_token: str
):
    create_resp = client.post("/requerimientos/", json=_BODY_VALIDO, headers=_auth(funcionario_token))
    req_id = create_resp.json()["id"]

    response = client.get(f"/requerimientos/{req_id}", headers=_auth(admin_token))
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "titulo" in data
    assert "estado" in data
    assert isinstance(data["historial"], list)


def test_obtener_detalle_requerimiento_inexistente(client: TestClient, admin_token: str):
    response = client.get("/requerimientos/9999", headers=_auth(admin_token))
    assert response.status_code == 404


def test_detalle_incluye_valores_adicionales(client: TestClient, db, admin_token: str, super_admin_token):
    from app.models.project_db import ProyectoDB

    sa_token, _ = super_admin_token
    proyecto_id = db.query(ProyectoDB).filter(ProyectoDB.nombre == "Proyecto Test").first().id

    auth_sa = {"Authorization": f"Bearer {sa_token}"}
    client.post(
        f"/proyectos/{proyecto_id}/campos",
        json={"nombre": "Contrato", "clave": "contrato", "tipo": "texto"},
        headers=auth_sa,
    )

    auth_admin = _auth(admin_token)
    create_resp = client.post(
        "/requerimientos/",
        json={**_BODY_VALIDO, "valores_adicionales": {"contrato": "CNT-001"}},
        headers=auth_admin,
    )
    req_id = create_resp.json()["id"]

    response = client.get(f"/requerimientos/{req_id}", headers=auth_admin)
    assert response.status_code == 200
    data = response.json()
    assert "valores_adicionales" in data
    assert data["valores_adicionales"].get("contrato") == "CNT-001"
