# -*- coding: utf-8 -*-
from app.schemas.api_schemas import CrearRequirementBody


def test_body_acepta_valores_adicionales():
    body = CrearRequirementBody(
        titulo="Error MGA",
        descripcion="El indicador no guarda",
        tipo="Bug",
        prioridad="Alta",
        valores_adicionales={"observaciones": "Nota interna", "proceso": "Informes"},
    )
    assert body.valores_adicionales == {"observaciones": "Nota interna", "proceso": "Informes"}


def test_body_valores_adicionales_default_es_dict_vacio():
    body = CrearRequirementBody(
        titulo="Error MGA",
        descripcion="El indicador no guarda",
        tipo="Bug",
        prioridad="Alta",
    )
    assert body.valores_adicionales == {}


def test_body_sin_valores_adicionales_no_rompe_validacion():
    body = CrearRequirementBody(
        titulo="T",
        descripcion="D",
        tipo="Nueva funcionalidad",
        prioridad="Baja",
    )
    assert isinstance(body.valores_adicionales, dict)
