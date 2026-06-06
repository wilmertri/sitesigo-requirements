# -*- coding: utf-8 -*-
from datetime import datetime

import pytest

from app.models.requirement import (
    EstadoRequerimiento,
    Requerimiento,
    RolUsuario,
)
from app.schemas.requirement_schema import Prioridad, TipoRequerimiento
from app.services.requirement_service import RequirementService


def _requerimiento_nuevo() -> Requerimiento:
    return Requerimiento(
        id=1,
        titulo="Modulo de reportes",
        descripcion="Exportar datos a Excel",
        tipo=TipoRequerimiento.nueva_funcionalidad,
        prioridad=Prioridad.media,
        autor_id=10,
        autor_rol=RolUsuario.funcionario,
        creado_en=datetime(2026, 6, 6, 9, 0, 0),
    )


def _requerimiento_con_estado(estado: EstadoRequerimiento) -> Requerimiento:
    req = _requerimiento_nuevo()
    req.estado = estado
    return req


def test_admin_puede_cambiar_estado():
    req = _requerimiento_nuevo()
    resultado = RequirementService.cambiar_estado(
        requerimiento=req,
        nuevo_estado=EstadoRequerimiento.en_analisis,
        rol_usuario=RolUsuario.administrador,
        usuario_id=1,
    )
    assert resultado.estado == EstadoRequerimiento.en_analisis


def test_funcionario_no_puede_cambiar_estado():
    req = _requerimiento_nuevo()
    with pytest.raises(PermissionError) as exc_info:
        RequirementService.cambiar_estado(
            requerimiento=req,
            nuevo_estado=EstadoRequerimiento.en_analisis,
            rol_usuario=RolUsuario.funcionario,
            usuario_id=1,
        )
    assert "Solo el Administrador puede cambiar el estado" in str(exc_info.value)


def test_equipo_tecnico_no_puede_cambiar_estado():
    req = _requerimiento_nuevo()
    with pytest.raises(PermissionError) as exc_info:
        RequirementService.cambiar_estado(
            requerimiento=req,
            nuevo_estado=EstadoRequerimiento.en_analisis,
            rol_usuario=RolUsuario.equipo_tecnico,
            usuario_id=1,
        )
    assert "Solo el Administrador puede cambiar el estado" in str(exc_info.value)


def test_estado_invalido_no_es_aceptado():
    req = _requerimiento_nuevo()
    with pytest.raises(ValueError):
        RequirementService.cambiar_estado(
            requerimiento=req,
            nuevo_estado="volando",
            rol_usuario=RolUsuario.administrador,
            usuario_id=1,
        )


def test_admin_no_puede_cambiar_estado_cerrado():
    req = _requerimiento_con_estado(EstadoRequerimiento.cerrado)
    with pytest.raises(ValueError) as exc_info:
        RequirementService.cambiar_estado(
            requerimiento=req,
            nuevo_estado=EstadoRequerimiento.resuelto,
            rol_usuario=RolUsuario.administrador,
            usuario_id=1,
        )
    assert "Un requerimiento Cerrado no puede cambiar de estado" in str(exc_info.value)


def test_admin_no_puede_cambiar_estado_rechazado():
    req = _requerimiento_con_estado(EstadoRequerimiento.rechazado)
    with pytest.raises(ValueError) as exc_info:
        RequirementService.cambiar_estado(
            requerimiento=req,
            nuevo_estado=EstadoRequerimiento.nuevo,
            rol_usuario=RolUsuario.administrador,
            usuario_id=1,
        )
    assert "Un requerimiento Rechazado no puede cambiar de estado" in str(exc_info.value)


def test_cambio_a_estado_terminal_es_permitido():
    req = _requerimiento_con_estado(EstadoRequerimiento.en_desarrollo)
    resultado = RequirementService.cambiar_estado(
        requerimiento=req,
        nuevo_estado=EstadoRequerimiento.cerrado,
        rol_usuario=RolUsuario.administrador,
        usuario_id=1,
    )
    assert resultado.estado == EstadoRequerimiento.cerrado
