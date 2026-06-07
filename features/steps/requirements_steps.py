# -*- coding: utf-8 -*-
from behave import given, when, then, use_step_matcher

use_step_matcher("re")


# ---------------------------------------------------------------------------
# Background / setup
# ---------------------------------------------------------------------------

@given(r'que existe un usuario admin registrado con email "(?P<email>[^"]*)" y password "(?P<password>[^"]*)" y rol "(?P<rol>[^"]*)"')
def step_registrar_admin(context, email, password, rol):
    context.admin_email = email
    context.admin_password = password
    context.client.post(
        "/auth/registro",
        json={"email": email, "password": password, "nombre": "Admin Test", "rol": rol},
    )


@given(r'que existe un usuario funcionario registrado con email "(?P<email>[^"]*)" y password "(?P<password>[^"]*)" y rol "(?P<rol>[^"]*)"')
def step_registrar_funcionario(context, email, password, rol):
    context.funcionario_email = email
    context.funcionario_password = password
    context.client.post(
        "/auth/registro",
        json={"email": email, "password": password, "nombre": "Funcionario Test", "rol": rol},
    )


# ---------------------------------------------------------------------------
# Autenticacion
# ---------------------------------------------------------------------------

@given(r"que estoy autenticado como admin")
def step_autenticar_admin(context):
    resp = context.client.post(
        "/auth/token",
        data={"username": context.admin_email, "password": context.admin_password},
    )
    assert resp.status_code == 200, f"Login admin fallo: {resp.json()}"
    context.token = resp.json()["access_token"]


@given(r"que estoy autenticado como funcionario")
def step_autenticar_funcionario(context):
    resp = context.client.post(
        "/auth/token",
        data={"username": context.funcionario_email, "password": context.funcionario_password},
    )
    assert resp.status_code == 200, f"Login funcionario fallo: {resp.json()}"
    context.token = resp.json()["access_token"]


# ---------------------------------------------------------------------------
# Creacion de requerimientos
# ---------------------------------------------------------------------------

@when(r'creo un requerimiento con titulo "(?P<titulo>[^"]*)" y descripcion "(?P<descripcion>[^"]*)" y tipo "(?P<tipo>[^"]*)" y prioridad "(?P<prioridad>[^"]*)"')
def step_crear_requerimiento(context, titulo, descripcion, tipo, prioridad):
    headers = {"Authorization": f"Bearer {context.token}"}
    context.response = context.client.post(
        "/requerimientos/",
        json={"titulo": titulo, "descripcion": descripcion, "tipo": tipo, "prioridad": prioridad},
        headers=headers,
    )
    if context.response.status_code == 201:
        context.requerimiento_id = context.response.json()["id"]


@given(r'existe un requerimiento en estado "(?P<estado>[^"]*)"')
def step_existe_requerimiento(context, estado):
    # Usa siempre admin para crear el req base (token puede no estar seteado aun)
    resp = context.client.post(
        "/auth/token",
        data={"username": context.admin_email, "password": context.admin_password},
    )
    admin_token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = context.client.post(
        "/requerimientos/",
        json={
            "titulo": "Requerimiento de prueba",
            "descripcion": "Descripcion de prueba para el escenario",
            "tipo": "Bug",
            "prioridad": "Media",
        },
        headers=headers,
    )
    assert resp.status_code == 201, f"No se pudo crear requerimiento base: {resp.json()}"
    context.requerimiento_id = resp.json()["id"]


# ---------------------------------------------------------------------------
# Cambio de estado
# ---------------------------------------------------------------------------

@when(r'el admin cambia el estado a "(?P<nuevo_estado>[^"]*)"')
def step_admin_cambia_estado(context, nuevo_estado):
    headers = {"Authorization": f"Bearer {context.token}"}
    context.response = context.client.patch(
        f"/requerimientos/{context.requerimiento_id}/estado",
        json={"nuevo_estado": nuevo_estado},
        headers=headers,
    )


@when(r'el admin intenta cambiar el estado a "(?P<nuevo_estado>[^"]*)"')
def step_admin_intenta_cambiar_estado(context, nuevo_estado):
    headers = {"Authorization": f"Bearer {context.token}"}
    context.response = context.client.patch(
        f"/requerimientos/{context.requerimiento_id}/estado",
        json={"nuevo_estado": nuevo_estado},
        headers=headers,
    )


@when(r'intento cambiar el estado a "(?P<nuevo_estado>[^"]*)"')
def step_intentar_cambiar_estado(context, nuevo_estado):
    headers = {"Authorization": f"Bearer {context.token}"}
    context.response = context.client.patch(
        f"/requerimientos/{context.requerimiento_id}/estado",
        json={"nuevo_estado": nuevo_estado},
        headers=headers,
    )


# ---------------------------------------------------------------------------
# Archivar
# ---------------------------------------------------------------------------

@when(r"el admin archiva el requerimiento")
def step_admin_archiva(context):
    headers = {"Authorization": f"Bearer {context.token}"}
    context.response = context.client.delete(
        f"/requerimientos/{context.requerimiento_id}",
        headers=headers,
    )


# ---------------------------------------------------------------------------
# Verificaciones
# ---------------------------------------------------------------------------

@then(r"la respuesta tiene codigo (?P<codigo>\d+)")
def step_verificar_codigo(context, codigo):
    assert context.response.status_code == int(codigo), (
        f"Esperado {codigo}, obtenido {context.response.status_code}. "
        f"Body: {context.response.text}"
    )


@then(r'el requerimiento se crea con estado "(?P<estado>[^"]*)"')
def step_verificar_estado_creacion(context, estado):
    assert context.response.json()["estado"] == estado, (
        f"Esperado estado '{estado}', obtenido '{context.response.json().get('estado')}'"
    )


@then(r'el requerimiento tiene estado "(?P<estado>[^"]*)"')
def step_verificar_estado(context, estado):
    assert context.response.json()["estado"] == estado, (
        f"Esperado estado '{estado}', obtenido '{context.response.json().get('estado')}'"
    )
