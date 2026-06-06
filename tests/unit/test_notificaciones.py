# -*- coding: utf-8 -*-
from datetime import datetime
from unittest.mock import patch

import pytest

from app.models.requirement import (
    EstadoRequerimiento,
    Requerimiento,
    RolUsuario,
)
from app.schemas.requirement_schema import Prioridad, TipoRequerimiento
from app.services.requirement_service import RequirementService


def _requerimiento(autor_rol: RolUsuario, autor_email: str = "") -> Requerimiento:
    return Requerimiento(
        id=1,
        titulo="Modulo de reportes",
        descripcion="Exportar datos a Excel",
        tipo=TipoRequerimiento.nueva_funcionalidad,
        prioridad=Prioridad.media,
        autor_id=10,
        autor_rol=autor_rol,
        creado_en=datetime(2026, 6, 6, 9, 0, 0),
        autor_email=autor_email,
    )


_PATCH_EMAIL = "app.services.notification_service.NotificationService.enviar_cambio_estado"


def test_cambio_estado_envia_email_si_autor_es_funcionario():
    req = _requerimiento(RolUsuario.funcionario, "funcionario@chia.gov.co")
    with patch(_PATCH_EMAIL) as mock_email:
        RequirementService.cambiar_estado(
            requerimiento=req,
            nuevo_estado=EstadoRequerimiento.resuelto,
            rol_usuario=RolUsuario.administrador,
            usuario_id=1,
        )
    mock_email.assert_called_once_with(
        email_destinatario="funcionario@chia.gov.co",
        titulo_requerimiento=req.titulo,
        estado_nuevo="Resuelto",
    )


def test_cambio_estado_no_envia_email_si_autor_es_admin():
    req = _requerimiento(RolUsuario.administrador)
    with patch(_PATCH_EMAIL) as mock_email:
        RequirementService.cambiar_estado(
            requerimiento=req,
            nuevo_estado=EstadoRequerimiento.en_analisis,
            rol_usuario=RolUsuario.administrador,
            usuario_id=1,
        )
    mock_email.assert_not_called()


def test_cambio_estado_no_envia_email_si_autor_es_equipo():
    req = _requerimiento(RolUsuario.equipo_tecnico)
    with patch(_PATCH_EMAIL) as mock_email:
        RequirementService.cambiar_estado(
            requerimiento=req,
            nuevo_estado=EstadoRequerimiento.en_analisis,
            rol_usuario=RolUsuario.administrador,
            usuario_id=1,
        )
    mock_email.assert_not_called()


def test_email_fallido_no_revierte_cambio_de_estado():
    req = _requerimiento(RolUsuario.funcionario, "funcionario@chia.gov.co")
    with patch(_PATCH_EMAIL, side_effect=Exception("SMTP error")):
        RequirementService.cambiar_estado(
            requerimiento=req,
            nuevo_estado=EstadoRequerimiento.en_analisis,
            rol_usuario=RolUsuario.administrador,
            usuario_id=1,
        )
    assert req.estado == EstadoRequerimiento.en_analisis
    assert len(req.historial) == 1
