# -*- coding: utf-8 -*-
import pytest
from datetime import datetime

from app.models.requirement import EstadoRequerimiento, Requerimiento, RolUsuario
from app.schemas.requirement_schema import Prioridad, TipoRequerimiento
from app.services.requirement_service import RequirementService


def _requerimiento(estado: EstadoRequerimiento) -> Requerimiento:
    return Requerimiento(
        id=1,
        titulo="Test",
        descripcion="Descripcion",
        tipo=TipoRequerimiento.bug,
        prioridad=Prioridad.media,
        autor_id=1,
        autor_rol=RolUsuario.funcionario,
        creado_en=datetime.now(),
        estado=estado,
    )


def test_admin_puede_archivar_requerimiento():
    req = _requerimiento(EstadoRequerimiento.nuevo)

    resultado = RequirementService.archivar(req, RolUsuario.administrador)

    assert resultado.estado == EstadoRequerimiento.archivado


def test_funcionario_no_puede_archivar():
    req = _requerimiento(EstadoRequerimiento.nuevo)

    with pytest.raises(PermissionError) as exc:
        RequirementService.archivar(req, RolUsuario.funcionario)

    assert "Solo el Administrador puede archivar requerimientos" in str(exc.value)


def test_archivar_requerimiento_ya_archivado_falla():
    req = _requerimiento(EstadoRequerimiento.archivado)

    with pytest.raises(ValueError) as exc:
        RequirementService.archivar(req, RolUsuario.administrador)

    assert "El requerimiento ya esta archivado" in str(exc.value)


def test_archivado_es_estado_terminal():
    req = _requerimiento(EstadoRequerimiento.archivado)

    with pytest.raises(ValueError):
        RequirementService.cambiar_estado(
            requerimiento=req,
            nuevo_estado=EstadoRequerimiento.nuevo,
            rol_usuario=RolUsuario.administrador,
            usuario_id=1,
        )
