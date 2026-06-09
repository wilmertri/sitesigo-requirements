# -*- coding: utf-8 -*-
import pytest
from pydantic import ValidationError
from app.schemas.config_schemas import EstadoConfigCreate
from app.services.config_service import ConfigService


# --- RN-24: cada proyecto tiene su lista de estados ---

def test_estado_valido_se_crea_correctamente():
    estado = EstadoConfigCreate(nombre="En Espera", color="#94a3b8")
    assert estado.nombre == "En Espera"
    assert estado.color == "#94a3b8"
    assert estado.es_terminal is False
    assert estado.orden == 0


def test_estado_terminal_se_crea_correctamente():
    estado = EstadoConfigCreate(nombre="Entregado", color="#10b981", es_terminal=True)
    assert estado.es_terminal is True


def test_nombre_vacio_es_rechazado():
    with pytest.raises(ValidationError):
        EstadoConfigCreate(nombre="", color="#94a3b8")


def test_color_invalido_es_rechazado():
    with pytest.raises(ValidationError):
        EstadoConfigCreate(nombre="En Espera", color="azul")


def test_color_sin_hash_es_rechazado():
    with pytest.raises(ValidationError):
        EstadoConfigCreate(nombre="En Espera", color="94a3b8")


def test_color_corto_es_rechazado():
    with pytest.raises(ValidationError):
        EstadoConfigCreate(nombre="En Espera", color="#94a3")


# --- RN-23: solo Super-Admin define estados ---

def test_super_admin_puede_definir_estados():
    assert ConfigService.puede_definir_estados("super_admin") is True


def test_admin_no_puede_definir_estados():
    assert ConfigService.puede_definir_estados("administrador") is False


def test_funcionario_no_puede_definir_estados():
    assert ConfigService.puede_definir_estados("funcionario") is False
