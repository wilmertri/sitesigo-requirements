# -*- coding: utf-8 -*-
from app.services.project_service import ProjectService


def test_super_admin_puede_crear_proyecto():
    assert ProjectService.puede_crear_proyecto("super_admin") is True


def test_admin_no_puede_crear_proyecto():
    assert ProjectService.puede_crear_proyecto("administrador") is False


def test_agregar_usuario_a_proyecto():
    assert ProjectService.puede_gestionar_usuarios("administrador") is True


def test_usuario_no_puede_acceder_a_otro_proyecto():
    assert ProjectService.puede_gestionar_usuarios("funcionario") is False
