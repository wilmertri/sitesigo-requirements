# -*- coding: utf-8 -*-
import pytest
from pydantic import ValidationError
from app.schemas.config_schemas import CampoConfigCreate
from app.services.config_service import ConfigService


# --- RN-21: tipos soportados ---

def test_campo_tipo_texto_es_valido():
    campo = CampoConfigCreate(nombre="Observaciones", clave="observaciones", tipo="texto")
    assert campo.tipo == "texto"


def test_campo_tipo_fecha_es_valido():
    campo = CampoConfigCreate(nombre="Fecha Inicio", clave="fecha_inicio", tipo="fecha")
    assert campo.tipo == "fecha"


def test_campo_tipo_numero_es_valido():
    campo = CampoConfigCreate(
        nombre="Obligacion contractual", clave="obligacion_contractual", tipo="numero"
    )
    assert campo.tipo == "numero"


def test_campo_tipo_lista_con_opciones_es_valido():
    campo = CampoConfigCreate(
        nombre="Proceso",
        clave="proceso",
        tipo="lista",
        opciones=["Seguimiento Fisico", "Informes"],
    )
    assert len(campo.opciones) == 2


def test_campo_tipo_calculado_es_valido():
    campo = CampoConfigCreate(nombre="Dias habiles", clave="dias_habiles", tipo="calculado")
    assert campo.tipo == "calculado"


def test_tipo_invalido_es_rechazado():
    with pytest.raises(ValidationError):
        CampoConfigCreate(nombre="X", clave="x", tipo="booleano")


def test_lista_sin_opciones_es_rechazada():
    with pytest.raises(ValidationError):
        CampoConfigCreate(nombre="Proceso", clave="proceso", tipo="lista", opciones=[])


def test_nombre_vacio_es_rechazado():
    with pytest.raises(ValidationError):
        CampoConfigCreate(nombre="", clave="proceso", tipo="texto")


def test_clave_vacia_es_rechazada():
    with pytest.raises(ValidationError):
        CampoConfigCreate(nombre="Proceso", clave="", tipo="texto")


# --- RN-20: solo Super-Admin define campos ---

def test_super_admin_puede_definir_campos():
    assert ConfigService.puede_definir_campos("super_admin") is True


def test_admin_no_puede_definir_campos():
    assert ConfigService.puede_definir_campos("administrador") is False


def test_funcionario_no_puede_definir_campos():
    assert ConfigService.puede_definir_campos("funcionario") is False
