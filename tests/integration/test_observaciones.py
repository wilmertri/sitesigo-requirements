# -*- coding: utf-8 -*-
from app.models.project_db import ProyectoDB
from app.models.requirement_db import CambioEstadoDB

_BODY = {
    "titulo": "Req obs",
    "descripcion": "Para probar observaciones",
    "tipo": "Bug",
    "prioridad": "Alta",
}


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _setup_campo_observaciones(client, db, sa_token):
    proyecto_id = db.query(ProyectoDB).filter(ProyectoDB.nombre == "Proyecto Test").first().id
    client.post(
        f"/proyectos/{proyecto_id}/campos",
        json={"nombre": "Observaciones", "clave": "observaciones", "tipo": "texto"},
        headers=_auth(sa_token),
    )


def _crear_req(client, token) -> int:
    resp = client.post("/requerimientos/", json=_BODY, headers=_auth(token))
    assert resp.status_code == 201
    return resp.json()["id"]


def test_creador_puede_editar_observaciones_en_estado_nuevo(
    client, db, funcionario_token, admin_token, super_admin_token
):
    sa_token, _ = super_admin_token
    _setup_campo_observaciones(client, db, sa_token)
    req_id = _crear_req(client, funcionario_token)

    resp = client.patch(
        f"/requerimientos/{req_id}/observaciones",
        json={"observaciones": "Revisar el modulo urgente"},
        headers=_auth(funcionario_token),
    )
    assert resp.status_code == 200


def test_creador_no_puede_editar_observaciones_en_estado_cerrado(
    client, db, funcionario_token, admin_token, super_admin_token
):
    sa_token, _ = super_admin_token
    _setup_campo_observaciones(client, db, sa_token)
    req_id = _crear_req(client, funcionario_token)

    client.patch(
        f"/requerimientos/{req_id}/estado",
        json={"nuevo_estado": "Cerrado"},
        headers=_auth(admin_token),
    )

    resp = client.patch(
        f"/requerimientos/{req_id}/observaciones",
        json={"observaciones": "Intentando editar en cerrado"},
        headers=_auth(funcionario_token),
    )
    assert resp.status_code == 422


def test_no_creador_recibe_403_en_observaciones(
    client, db, funcionario_token, admin_token, super_admin_token
):
    sa_token, _ = super_admin_token
    _setup_campo_observaciones(client, db, sa_token)
    req_id = _crear_req(client, funcionario_token)

    # admin no es el creador → 403
    resp = client.patch(
        f"/requerimientos/{req_id}/observaciones",
        json={"observaciones": "Intento de admin"},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 403


def test_editar_observaciones_registra_en_historial(
    client, db, funcionario_token, admin_token, super_admin_token
):
    sa_token, _ = super_admin_token
    _setup_campo_observaciones(client, db, sa_token)
    req_id = _crear_req(client, funcionario_token)

    client.patch(
        f"/requerimientos/{req_id}/observaciones",
        json={"observaciones": "Nueva observacion"},
        headers=_auth(funcionario_token),
    )

    historial = (
        db.query(CambioEstadoDB)
        .filter(CambioEstadoDB.requerimiento_id == req_id)
        .all()
    )
    assert len(historial) == 1
    assert historial[0].estado_nuevo == "Observaciones actualizadas"
