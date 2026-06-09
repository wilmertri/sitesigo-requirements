# -*- coding: utf-8 -*-
from app.models.config_db import RequerimientoValorCampoDB
from app.repositories.config_repository import ConfigRepository
from app.schemas.config_schemas import CampoConfigCreate


def test_post_requerimiento_persiste_valores_adicionales(client, db, admin_token, super_admin_token):
    sa_token, _ = super_admin_token

    # el admin tiene su propio proyecto; obtenemos su id desde la BD
    from app.models.project_db import ProyectoDB
    proyecto_admin = db.query(ProyectoDB).filter(ProyectoDB.nombre == "Proyecto Test").first()
    proyecto_id = proyecto_admin.id

    # super_admin configura campos en el proyecto del admin
    auth_sa = {"Authorization": f"Bearer {sa_token}"}
    client.post(f"/proyectos/{proyecto_id}/campos",
                json={"nombre": "Observaciones", "clave": "observaciones", "tipo": "texto"},
                headers=auth_sa)
    client.post(f"/proyectos/{proyecto_id}/campos",
                json={"nombre": "Proceso", "clave": "proceso", "tipo": "lista",
                      "opciones": ["Informes", "Todos"]},
                headers=auth_sa)

    # admin crea requerimiento con valores adicionales
    auth_admin = {"Authorization": f"Bearer {admin_token}"}
    resp = client.post(
        "/requerimientos/",
        json={
            "titulo": "Error en MGA",
            "descripcion": "El indicador no guarda el valor",
            "tipo": "Bug",
            "prioridad": "Alta",
            "valores_adicionales": {
                "observaciones": "Revisar urgente",
                "proceso": "Informes",
            },
        },
        headers=auth_admin,
    )

    assert resp.status_code == 201
    req_id = resp.json()["id"]

    valores = db.query(RequerimientoValorCampoDB).filter(
        RequerimientoValorCampoDB.requerimiento_id == req_id
    ).all()

    assert len(valores) == 2
    valores_dict = {v.campo_id: v.valor for v in valores}
    assert "Revisar urgente" in valores_dict.values()
    assert "Informes" in valores_dict.values()


def test_post_requerimiento_sin_valores_adicionales_funciona_igual(client, admin_token):
    auth = {"Authorization": f"Bearer {admin_token}"}
    resp = client.post(
        "/requerimientos/",
        json={
            "titulo": "Sin campos extra",
            "descripcion": "Requerimiento normal",
            "tipo": "Bug",
            "prioridad": "Media",
        },
        headers=auth,
    )
    assert resp.status_code == 201


def test_clave_inexistente_es_ignorada(client, db, admin_token, super_admin_token):
    sa_token, proyecto_id = super_admin_token
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    resp = client.post(
        "/requerimientos/",
        json={
            "titulo": "Test clave",
            "descripcion": "Clave que no existe",
            "tipo": "Bug",
            "prioridad": "Baja",
            "valores_adicionales": {"clave_fantasma": "valor"},
        },
        headers=auth_admin,
    )

    assert resp.status_code == 201
    req_id = resp.json()["id"]

    valores = db.query(RequerimientoValorCampoDB).filter(
        RequerimientoValorCampoDB.requerimiento_id == req_id
    ).all()
    assert len(valores) == 0
