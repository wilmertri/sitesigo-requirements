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


def test_cambio_de_estado_registra_historial():
    req = _requerimiento_nuevo()
    RequirementService.cambiar_estado(
        requerimiento=req,
        nuevo_estado=EstadoRequerimiento.en_analisis,
        rol_usuario=RolUsuario.administrador,
        usuario_id=42,
    )
    assert len(req.historial) == 1
    entrada = req.historial[0]
    assert entrada.estado_anterior == EstadoRequerimiento.nuevo
    assert entrada.estado_nuevo == EstadoRequerimiento.en_analisis
    assert entrada.rol_usuario == RolUsuario.administrador


def test_historial_acumula_multiples_cambios():
    req = _requerimiento_nuevo()
    RequirementService.cambiar_estado(
        requerimiento=req,
        nuevo_estado=EstadoRequerimiento.en_analisis,
        rol_usuario=RolUsuario.administrador,
        usuario_id=42,
    )
    RequirementService.cambiar_estado(
        requerimiento=req,
        nuevo_estado=EstadoRequerimiento.en_desarrollo,
        rol_usuario=RolUsuario.administrador,
        usuario_id=42,
    )
    assert len(req.historial) == 2
    assert req.historial[0].estado_nuevo == EstadoRequerimiento.en_analisis
    assert req.historial[1].estado_nuevo == EstadoRequerimiento.en_desarrollo


def test_cambio_fallido_no_registra_historial():
    req = _requerimiento_nuevo()
    with pytest.raises(PermissionError):
        RequirementService.cambiar_estado(
            requerimiento=req,
            nuevo_estado=EstadoRequerimiento.en_analisis,
            rol_usuario=RolUsuario.funcionario,
            usuario_id=10,
        )
    assert len(req.historial) == 0


def test_historial_registra_usuario_correcto():
    req = _requerimiento_nuevo()
    RequirementService.cambiar_estado(
        requerimiento=req,
        nuevo_estado=EstadoRequerimiento.en_analisis,
        rol_usuario=RolUsuario.administrador,
        usuario_id=42,
    )
    assert req.historial[0].usuario_id == 42
