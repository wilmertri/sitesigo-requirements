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


def _requerimiento(estado: EstadoRequerimiento, autor_id: int) -> Requerimiento:
    return Requerimiento(
        id=1,
        titulo="Modulo de reportes",
        descripcion="Descripcion original",
        tipo=TipoRequerimiento.nueva_funcionalidad,
        prioridad=Prioridad.media,
        autor_id=autor_id,
        autor_rol=RolUsuario.funcionario,
        creado_en=datetime(2026, 6, 6, 9, 0, 0),
        estado=estado,
    )


def test_funcionario_edita_su_requerimiento_en_estado_nuevo():
    req = _requerimiento(EstadoRequerimiento.nuevo, autor_id=1)
    resultado = RequirementService.editar(
        requerimiento=req,
        nueva_descripcion="Descripcion actualizada",
        usuario_id=1,
        rol_usuario=RolUsuario.funcionario,
    )
    assert resultado.descripcion == "Descripcion actualizada"


def test_funcionario_no_puede_editar_requerimiento_ajeno():
    req = _requerimiento(EstadoRequerimiento.nuevo, autor_id=1)
    with pytest.raises(PermissionError) as exc_info:
        RequirementService.editar(
            requerimiento=req,
            nueva_descripcion="Intento de edicion",
            usuario_id=2,
            rol_usuario=RolUsuario.funcionario,
        )
    assert "Solo puedes editar tus propios requerimientos" in str(exc_info.value)


def test_funcionario_no_puede_editar_en_estado_en_analisis():
    req = _requerimiento(EstadoRequerimiento.en_analisis, autor_id=1)
    with pytest.raises(PermissionError) as exc_info:
        RequirementService.editar(
            requerimiento=req,
            nueva_descripcion="Intento de edicion",
            usuario_id=1,
            rol_usuario=RolUsuario.funcionario,
        )
    assert "Solo puedes editar requerimientos en estado Nuevo" in str(exc_info.value)


def test_admin_puede_editar_cualquier_requerimiento():
    req = _requerimiento(EstadoRequerimiento.en_desarrollo, autor_id=1)
    resultado = RequirementService.editar(
        requerimiento=req,
        nueva_descripcion="Edicion del admin",
        usuario_id=99,
        rol_usuario=RolUsuario.administrador,
    )
    assert resultado.descripcion == "Edicion del admin"


def test_nadie_puede_editar_requerimiento_cerrado():
    req = _requerimiento(EstadoRequerimiento.cerrado, autor_id=1)
    with pytest.raises(ValueError) as exc_info:
        RequirementService.editar(
            requerimiento=req,
            nueva_descripcion="Intento sobre cerrado",
            usuario_id=99,
            rol_usuario=RolUsuario.administrador,
        )
    assert "Un requerimiento Cerrado no puede ser editado" in str(exc_info.value)
