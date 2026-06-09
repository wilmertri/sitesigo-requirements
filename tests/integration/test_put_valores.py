# -*- coding: utf-8 -*-
from app.models.config_db import RequerimientoValorCampoDB
from app.models.project_db import ProyectoDB


# helpers -------------------------------------------------------------------

def _proyecto_admin_id(db):
    return db.query(ProyectoDB).filter(ProyectoDB.nombre == "Proyecto Test").first().id


def _setup_campos(client, sa_token, proyecto_id):
    auth = {"Authorization": f"Bearer {sa_token}"}
    client.post(f"/proyectos/{proyecto_id}/campos",
                json={"nombre": "Observaciones", "clave": "observaciones", "tipo": "texto"},
                headers=auth)
    client.post(f"/proyectos/{proyecto_id}/campos",
                json={"nombre": "Proceso", "clave": "proceso",
                      "tipo": "lista", "opciones": ["Informes", "Todos"]},
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

def test_admin_actualiza_valor_existente(client, db, admin_token, super_admin_token):
    sa_token, _ = super_admin_token
    pid = _proyecto_admin_id(db)
    _setup_campos(client, sa_token, pid)
    req_id = _crear_req(client, admin_token)

    # insertar valor inicial
    client.put(
        f"/requerimientos/{req_id}/valores",
        json={"valores_adicionales": {"observaciones": "inicial"}},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # actualizar
    resp = client.put(
        f"/requerimientos/{req_id}/valores",
        json={"valores_adicionales": {"observaciones": "actualizado"}},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200

    valores = db.query(RequerimientoValorCampoDB).filter(
        RequerimientoValorCampoDB.requerimiento_id == req_id
    ).all()
    assert len(valores) == 1
    assert valores[0].valor == "actualizado"


def test_admin_inserta_valor_nuevo(client, db, admin_token, super_admin_token):
    sa_token, _ = super_admin_token
    pid = _proyecto_admin_id(db)
    _setup_campos(client, sa_token, pid)
    req_id = _crear_req(client, admin_token)

    resp = client.put(
        f"/requerimientos/{req_id}/valores",
        json={"valores_adicionales": {"observaciones": "nuevo", "proceso": "Informes"}},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200

    valores = db.query(RequerimientoValorCampoDB).filter(
        RequerimientoValorCampoDB.requerimiento_id == req_id
    ).all()
    assert len(valores) == 2


def test_creador_puede_actualizar_sus_valores(client, db, funcionario_token, admin_token, super_admin_token):
    sa_token, _ = super_admin_token
    pid = _proyecto_admin_id(db)
    _setup_campos(client, sa_token, pid)
    req_id = _crear_req(client, funcionario_token)

    resp = client.put(
        f"/requerimientos/{req_id}/valores",
        json={"valores_adicionales": {"observaciones": "del funcionario"}},
        headers={"Authorization": f"Bearer {funcionario_token}"},
    )
    assert resp.status_code == 200


def test_funcionario_no_creador_no_puede_actualizar(client, db, funcionario_token, admin_token, super_admin_token):
    sa_token, _ = super_admin_token
    pid = _proyecto_admin_id(db)
    _setup_campos(client, sa_token, pid)
    # admin crea el requerimiento
    req_id = _crear_req(client, admin_token)

    # funcionario (no creador) intenta actualizar
    resp = client.put(
        f"/requerimientos/{req_id}/valores",
        json={"valores_adicionales": {"observaciones": "intento"}},
        headers={"Authorization": f"Bearer {funcionario_token}"},
    )
    assert resp.status_code == 403


def test_clave_inexistente_es_ignorada_en_put(client, db, admin_token, super_admin_token):
    sa_token, _ = super_admin_token
    pid = _proyecto_admin_id(db)
    _setup_campos(client, sa_token, pid)
    req_id = _crear_req(client, admin_token)

    resp = client.put(
        f"/requerimientos/{req_id}/valores",
        json={"valores_adicionales": {"clave_fantasma": "x"}},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    valores = db.query(RequerimientoValorCampoDB).filter(
        RequerimientoValorCampoDB.requerimiento_id == req_id
    ).all()
    assert len(valores) == 0


def test_put_valores_req_no_encontrado(client, admin_token):
    resp = client.put(
        "/requerimientos/9999/valores",
        json={"valores_adicionales": {"observaciones": "x"}},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404
