# -*- coding: utf-8 -*-
from behave import given, when, then, use_step_matcher

use_step_matcher("re")


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

@given(r'que el primer usuario es super_admin con email "(?P<email>[^"]*)" y password "(?P<password>[^"]*)"')
def step_registrar_super_admin(context, email, password):
    context.sa_email = email
    context.sa_password = password
    context.client.post(
        "/auth/registro",
        json={"email": email, "password": password, "nombre": "Super Admin", "rol": "super_admin"},
    )


@given(r'que el super_admin crea el proyecto "(?P<nombre>[^"]*)"')
def step_super_admin_crea_proyecto(context, nombre):
    resp = context.client.post(
        "/auth/token",
        data={"username": context.sa_email, "password": context.sa_password},
    )
    sa_token = resp.json()["access_token"]
    resp = context.client.post(
        "/proyectos/",
        json={"nombre": nombre},
        headers={"Authorization": f"Bearer {sa_token}"},
    )
    assert resp.status_code == 201, f"No se pudo crear proyecto: {resp.json()}"
    context.proyecto_id = resp.json()["id"]


@given(r'que existe un admin en el proyecto con email "(?P<email>[^"]*)" y password "(?P<password>[^"]*)"')
def step_registrar_admin_en_proyecto(context, email, password):
    context.admin_email = email
    context.admin_password = password
    resp = context.client.post(
        "/auth/token",
        data={"username": context.sa_email, "password": context.sa_password},
    )
    sa_token = resp.json()["access_token"]
    context.client.post(
        f"/proyectos/{context.proyecto_id}/usuarios",
        json={"email": email, "rol": "administrador", "nombre": "Admin Test", "password": password},
        headers={"Authorization": f"Bearer {sa_token}"},
    )


# ---------------------------------------------------------------------------
# Autenticacion
# ---------------------------------------------------------------------------

@given(r"que estoy autenticado como super_admin")
def step_autenticar_super_admin(context):
    resp = context.client.post(
        "/auth/token",
        data={"username": context.sa_email, "password": context.sa_password},
    )
    assert resp.status_code == 200, f"Login super_admin fallo: {resp.json()}"
    context.token = resp.json()["access_token"]


@given(r"que estoy autenticado como admin en el proyecto")
def step_autenticar_admin_proyecto(context):
    resp = context.client.post(
        "/auth/token",
        data={"username": context.admin_email, "password": context.admin_password},
    )
    assert resp.status_code == 200, f"Login admin fallo: {resp.json()}"
    context.token = resp.json()["access_token"]


# ---------------------------------------------------------------------------
# Campos
# ---------------------------------------------------------------------------

@when(r'creo un campo con nombre "(?P<nombre>[^"]*)" y clave "(?P<clave>[^"]*)" y tipo "(?P<tipo>[^"]*)"')
def step_crear_campo(context, nombre, clave, tipo):
    context.response = context.client.post(
        f"/proyectos/{context.proyecto_id}/campos",
        json={"nombre": nombre, "clave": clave, "tipo": tipo},
        headers={"Authorization": f"Bearer {context.token}"},
    )


@when(r'creo un campo de lista con nombre "(?P<nombre>[^"]*)" y clave "(?P<clave>[^"]*)" y opciones "(?P<opciones>[^"]*)"')
def step_crear_campo_lista(context, nombre, clave, opciones):
    context.response = context.client.post(
        f"/proyectos/{context.proyecto_id}/campos",
        json={"nombre": nombre, "clave": clave, "tipo": "lista",
              "opciones": opciones.split(",")},
        headers={"Authorization": f"Bearer {context.token}"},
    )


@when(r'creo un campo de lista sin opciones con nombre "(?P<nombre>[^"]*)" y clave "(?P<clave>[^"]*)"')
def step_crear_campo_lista_sin_opciones(context, nombre, clave):
    context.response = context.client.post(
        f"/proyectos/{context.proyecto_id}/campos",
        json={"nombre": nombre, "clave": clave, "tipo": "lista", "opciones": []},
        headers={"Authorization": f"Bearer {context.token}"},
    )


@when(r'intento crear un campo con nombre "(?P<nombre>[^"]*)" y clave "(?P<clave>[^"]*)" y tipo "(?P<tipo>[^"]*)"')
def step_intentar_crear_campo(context, nombre, clave, tipo):
    context.response = context.client.post(
        f"/proyectos/{context.proyecto_id}/campos",
        json={"nombre": nombre, "clave": clave, "tipo": tipo},
        headers={"Authorization": f"Bearer {context.token}"},
    )


# ---------------------------------------------------------------------------
# Estados
# ---------------------------------------------------------------------------

@when(r'creo un estado con nombre "(?P<nombre>[^"]*)" y color "(?P<color>[^"]*)"')
def step_crear_estado(context, nombre, color):
    context.response = context.client.post(
        f"/proyectos/{context.proyecto_id}/estados",
        json={"nombre": nombre, "color": color},
        headers={"Authorization": f"Bearer {context.token}"},
    )


@when(r'creo un estado terminal con nombre "(?P<nombre>[^"]*)" y color "(?P<color>[^"]*)"')
def step_crear_estado_terminal(context, nombre, color):
    context.response = context.client.post(
        f"/proyectos/{context.proyecto_id}/estados",
        json={"nombre": nombre, "color": color, "es_terminal": True},
        headers={"Authorization": f"Bearer {context.token}"},
    )


@when(r'intento crear un estado con nombre "(?P<nombre>[^"]*)" y color "(?P<color>[^"]*)"')
def step_intentar_crear_estado(context, nombre, color):
    context.response = context.client.post(
        f"/proyectos/{context.proyecto_id}/estados",
        json={"nombre": nombre, "color": color},
        headers={"Authorization": f"Bearer {context.token}"},
    )


# ---------------------------------------------------------------------------
# Dias habiles
# ---------------------------------------------------------------------------

@when(r'calculo dias habiles entre "(?P<inicio>[^"]*)" y "(?P<final>[^"]*)"')
def step_calcular_dias_habiles(context, inicio, final):
    context.response = context.client.get(
        f"/proyectos/{context.proyecto_id}/dias-habiles",
        params={"fecha_inicio": inicio, "fecha_final": final},
        headers={"Authorization": f"Bearer {context.token}"},
    )


# ---------------------------------------------------------------------------
# Verificaciones
# ---------------------------------------------------------------------------

@then(r'el campo tiene tipo "(?P<tipo>[^"]*)"')
def step_verificar_tipo_campo(context, tipo):
    assert context.response.json()["tipo"] == tipo, (
        f"Esperado tipo '{tipo}', obtenido '{context.response.json().get('tipo')}'"
    )


@then(r'el estado tiene nombre "(?P<nombre>[^"]*)"')
def step_verificar_nombre_estado(context, nombre):
    assert context.response.json()["nombre"] == nombre, (
        f"Esperado nombre '{nombre}', obtenido '{context.response.json().get('nombre')}'"
    )


@then(r"el estado es terminal")
def step_verificar_terminal(context):
    assert context.response.json()["es_terminal"] is True, "Se esperaba es_terminal=True"


@then(r"el estado no es terminal")
def step_verificar_no_terminal(context):
    assert context.response.json()["es_terminal"] is False, "Se esperaba es_terminal=False"


@then(r"los dias habiles son (?P<n>\d+)")
def step_verificar_dias_habiles(context, n):
    assert context.response.json()["dias_habiles"] == int(n), (
        f"Esperado {n}, obtenido {context.response.json().get('dias_habiles')}"
    )
