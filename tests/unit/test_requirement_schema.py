# -*- coding: utf-8 -*-
import pytest
from pydantic import ValidationError
from app.schemas.requirement_schema import (
    RequirementCreate,
    Prioridad,
    TipoRequerimiento,
)


def test_requerimiento_valido_se_crea_correctamente():
    req = RequirementCreate(
        titulo="Login de usuario",
        descripcion="Permitir autenticacion con email y password",
        tipo=TipoRequerimiento.nueva_funcionalidad,
        prioridad=Prioridad.alta,
    )
    assert req.titulo == "Login de usuario"
    assert req.tipo == TipoRequerimiento.nueva_funcionalidad
    assert req.prioridad == Prioridad.alta


def test_descripcion_vacia_falla():
    with pytest.raises(ValidationError) as exc_info:
        RequirementCreate(
            titulo="Login de usuario",
            descripcion="",
            tipo=TipoRequerimiento.bug,
            prioridad=Prioridad.media,
        )
    assert "La descripcion es obligatoria" in str(exc_info.value)


def test_descripcion_solo_espacios_falla():
    with pytest.raises(ValidationError):
        RequirementCreate(
            titulo="Login de usuario",
            descripcion="   ",
            tipo=TipoRequerimiento.bug,
            prioridad=Prioridad.baja,
        )


def test_prioridad_invalida_falla():
    with pytest.raises(ValidationError):
        RequirementCreate(
            titulo="Login de usuario",
            descripcion="Descripcion valida",
            tipo=TipoRequerimiento.bug,
            prioridad="Urgente",
        )


def test_tipo_invalido_falla():
    with pytest.raises(ValidationError):
        RequirementCreate(
            titulo="Login de usuario",
            descripcion="Descripcion valida",
            tipo="Soporte tecnico",
            prioridad=Prioridad.alta,
        )


def test_titulo_no_puede_estar_vacio():
    with pytest.raises(ValidationError) as exc_info:
        RequirementCreate(
            titulo="",
            descripcion="Descripcion valida",
            tipo=TipoRequerimiento.mejora_ux_rendimiento,
            prioridad=Prioridad.baja,
        )
    assert "El titulo es obligatorio" in str(exc_info.value)