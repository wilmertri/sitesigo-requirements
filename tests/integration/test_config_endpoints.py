# -*- coding: utf-8 -*-


# --- campos ---

def test_super_admin_crea_campo(client, super_admin_token):
    token, proyecto_id = super_admin_token
    resp = client.post(
        f"/proyectos/{proyecto_id}/campos",
        json={"nombre": "Observaciones", "clave": "observaciones", "tipo": "texto"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["nombre"] == "Observaciones"
    assert data["tipo"] == "texto"
    assert data["proyecto_id"] == proyecto_id


def test_admin_no_puede_crear_campo(client, admin_token):
    resp = client.post(
        "/proyectos/1/campos",
        json={"nombre": "Campo", "clave": "campo", "tipo": "texto"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 403


def test_crear_campo_tipo_invalido(client, super_admin_token):
    token, proyecto_id = super_admin_token
    resp = client.post(
        f"/proyectos/{proyecto_id}/campos",
        json={"nombre": "X", "clave": "x", "tipo": "booleano"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


def test_crear_campo_lista_sin_opciones(client, super_admin_token):
    token, proyecto_id = super_admin_token
    resp = client.post(
        f"/proyectos/{proyecto_id}/campos",
        json={"nombre": "Proceso", "clave": "proceso", "tipo": "lista", "opciones": []},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


def test_listar_campos_del_proyecto(client, super_admin_token):
    token, proyecto_id = super_admin_token
    auth = {"Authorization": f"Bearer {token}"}

    client.post(f"/proyectos/{proyecto_id}/campos",
                json={"nombre": "Obs", "clave": "obs", "tipo": "texto"}, headers=auth)
    client.post(f"/proyectos/{proyecto_id}/campos",
                json={"nombre": "Proceso", "clave": "proceso", "tipo": "lista",
                      "opciones": ["A", "B"]}, headers=auth)

    resp = client.get(f"/proyectos/{proyecto_id}/campos", headers=auth)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


# --- estados ---

def test_super_admin_crea_estado(client, super_admin_token):
    token, proyecto_id = super_admin_token
    resp = client.post(
        f"/proyectos/{proyecto_id}/estados",
        json={"nombre": "En Espera", "color": "#94a3b8"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["nombre"] == "En Espera"
    assert data["color"] == "#94a3b8"
    assert data["es_terminal"] is False


def test_admin_no_puede_crear_estado(client, admin_token):
    resp = client.post(
        "/proyectos/1/estados",
        json={"nombre": "Estado", "color": "#ffffff"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 403


def test_crear_estado_color_invalido(client, super_admin_token):
    token, proyecto_id = super_admin_token
    resp = client.post(
        f"/proyectos/{proyecto_id}/estados",
        json={"nombre": "Estado", "color": "rojo"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


def test_listar_estados_del_proyecto(client, super_admin_token):
    token, proyecto_id = super_admin_token
    auth = {"Authorization": f"Bearer {token}"}

    for nombre, color in [("En Espera", "#94a3b8"), ("Entregado", "#10b981")]:
        client.post(f"/proyectos/{proyecto_id}/estados",
                    json={"nombre": nombre, "color": color}, headers=auth)

    resp = client.get(f"/proyectos/{proyecto_id}/estados", headers=auth)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


# --- dias habiles ---

def test_calcular_dias_habiles(client, super_admin_token):
    token, proyecto_id = super_admin_token
    resp = client.get(
        f"/proyectos/{proyecto_id}/dias-habiles",
        params={"fecha_inicio": "2026-01-05", "fecha_final": "2026-01-12"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["dias_habiles"] == 5


def test_calcular_dias_habiles_fechas_invalidas(client, super_admin_token):
    token, proyecto_id = super_admin_token
    resp = client.get(
        f"/proyectos/{proyecto_id}/dias-habiles",
        params={"fecha_inicio": "no-es-fecha", "fecha_final": "2026-01-12"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
