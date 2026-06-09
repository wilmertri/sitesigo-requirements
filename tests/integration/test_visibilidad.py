# -*- coding: utf-8 -*-
from app.auth.jwt_handler import crear_token
from app.auth.password_handler import hashear_password
from app.models.project_db import ProyectoDB, UsuarioProyectoDB
from app.models.user_db import UsuarioDB

_BODY = {
    "titulo": "Req de prueba",
    "descripcion": "Descripcion",
    "tipo": "Bug",
    "prioridad": "Media",
}


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _crear_funcionario_b(db) -> str:
    proyecto = db.query(ProyectoDB).filter(ProyectoDB.nombre == "Proyecto Test").first()
    func2 = UsuarioDB(
        email="func2@test.com",
        hashed_password=hashear_password("x"),
        rol="funcionario",
        nombre="Funcionario B",
        activo=True,
    )
    db.add(func2)
    db.commit()
    db.refresh(func2)
    db.add(UsuarioProyectoDB(
        usuario_id=func2.id,
        proyecto_id=proyecto.id,
        rol="funcionario",
        activo=True,
    ))
    db.commit()
    return crear_token({
        "sub": str(func2.id),
        "email": func2.email,
        "rol": "funcionario",
        "nombre": func2.nombre,
        "proyecto_id": proyecto.id,
    })


def test_funcionario_solo_ve_sus_requerimientos(client, db, funcionario_token, admin_token):
    # funcionario A crea un requerimiento
    client.post("/requerimientos/", json=_BODY, headers=_auth(funcionario_token))

    # funcionario B no ha creado nada — debe ver lista vacia
    token_b = _crear_funcionario_b(db)
    resp = client.get("/requerimientos/", headers=_auth(token_b))
    assert resp.status_code == 200
    assert len(resp.json()) == 0


def test_admin_ve_todos_los_requerimientos_del_proyecto(client, funcionario_token, admin_token):
    client.post("/requerimientos/", json=_BODY, headers=_auth(funcionario_token))
    client.post("/requerimientos/", json=_BODY, headers=_auth(admin_token))

    resp = client.get("/requerimientos/", headers=_auth(admin_token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_super_admin_ve_requerimientos_de_todos_los_proyectos(
    client, admin_token, super_admin_token
):
    sa_token, _ = super_admin_token
    # admin crea req en "Proyecto Test"
    client.post("/requerimientos/", json=_BODY, headers=_auth(admin_token))

    # super_admin tiene proyecto_id de "Proyecto SA Test" — debe ver igualmente el req de admin
    resp = client.get("/requerimientos/", headers=_auth(sa_token))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
