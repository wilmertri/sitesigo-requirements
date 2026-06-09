# -*- coding: utf-8 -*-
from app.models.project_db import ProyectoDB
from app.models.requirement_db import CambioEstadoDB, RequerimientooDB


def _proyecto_admin_id(db):
    return db.query(ProyectoDB).filter(ProyectoDB.nombre == "Proyecto Test").first().id


def _setup_estados(client, sa_token, proyecto_id):
    auth = {"Authorization": f"Bearer {sa_token}"}
    client.post(f"/proyectos/{proyecto_id}/estados",
                json={"nombre": "En Revision", "color": "#f59e0b"},
                headers=auth)
    client.post(f"/proyectos/{proyecto_id}/estados",
                json={"nombre": "Entregado", "color": "#10b981", "es_terminal": True},
                headers=auth)


def _crear_req(client, token):
    resp = client.post(
        "/requerimientos/",
        json={"titulo": "T", "descripcion": "D", "tipo": "Bug", "prioridad": "Alta"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


# tests ---------------------------------------------------------------------

def test_admin_cambia_estado_proyecto(client, db, admin_token, super_admin_token):
    sa_token, _ = super_admin_token
    pid = _proyecto_admin_id(db)
    _setup_estados(client, sa_token, pid)
    req_id = _crear_req(client, admin_token)

    resp = client.patch(
        f"/requerimientos/{req_id}/estado-proyecto",
        json={"estado_proyecto": "En Revision"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["estado_proyecto"] == "En Revision"


def test_cambio_estado_proyecto_queda_en_historial(client, db, admin_token, super_admin_token):
    sa_token, _ = super_admin_token
    pid = _proyecto_admin_id(db)
    _setup_estados(client, sa_token, pid)
    req_id = _crear_req(client, admin_token)

    client.patch(
        f"/requerimientos/{req_id}/estado-proyecto",
        json={"estado_proyecto": "En Revision"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    historial = db.query(CambioEstadoDB).filter(
        CambioEstadoDB.requerimiento_id == req_id
    ).all()
    assert len(historial) == 1
    assert historial[0].estado_nuevo == "En Revision"


def test_estado_proyecto_inexistente_retorna_422(client, db, admin_token, super_admin_token):
    sa_token, _ = super_admin_token
    pid = _proyecto_admin_id(db)
    _setup_estados(client, sa_token, pid)
    req_id = _crear_req(client, admin_token)

    resp = client.patch(
        f"/requerimientos/{req_id}/estado-proyecto",
        json={"estado_proyecto": "Estado Fantasma"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 422


def test_funcionario_no_puede_cambiar_estado_proyecto(client, db, funcionario_token, admin_token, super_admin_token):
    sa_token, _ = super_admin_token
    pid = _proyecto_admin_id(db)
    _setup_estados(client, sa_token, pid)
    req_id = _crear_req(client, admin_token)

    resp = client.patch(
        f"/requerimientos/{req_id}/estado-proyecto",
        json={"estado_proyecto": "En Revision"},
        headers={"Authorization": f"Bearer {funcionario_token}"},
    )
    assert resp.status_code == 403


def test_estado_proyecto_req_no_encontrado(client, admin_token):
    resp = client.patch(
        "/requerimientos/9999/estado-proyecto",
        json={"estado_proyecto": "En Revision"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404


def test_segundo_cambio_actualiza_estado_proyecto(client, db, admin_token, super_admin_token):
    sa_token, _ = super_admin_token
    pid = _proyecto_admin_id(db)
    _setup_estados(client, sa_token, pid)
    req_id = _crear_req(client, admin_token)

    client.patch(
        f"/requerimientos/{req_id}/estado-proyecto",
        json={"estado_proyecto": "En Revision"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = client.patch(
        f"/requerimientos/{req_id}/estado-proyecto",
        json={"estado_proyecto": "Entregado"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["estado_proyecto"] == "Entregado"

    historial = db.query(CambioEstadoDB).filter(
        CambioEstadoDB.requerimiento_id == req_id
    ).all()
    assert len(historial) == 2
    assert historial[1].estado_anterior == "En Revision"
    assert historial[1].estado_nuevo == "Entregado"
