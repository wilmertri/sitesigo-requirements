# -*- coding: utf-8 -*-
from app.auth.jwt_handler import crear_token, verificar_token
from app.auth.password_handler import hashear_password, verificar_password


def test_hashear_password_no_devuelve_texto_plano():
    hashed = hashear_password("mi_password")
    assert hashed != "mi_password"


def test_verificar_password_correcto():
    hashed = hashear_password("mi_password")
    assert verificar_password("mi_password", hashed) is True


def test_verificar_password_incorrecto():
    hashed = hashear_password("mi_password")
    assert verificar_password("otro", hashed) is False


def test_crear_token_devuelve_string():
    token = crear_token({"sub": "1", "rol": "administrador"})
    assert isinstance(token, str)
    assert len(token) > 0


def test_verificar_token_valido():
    data = {"sub": "1", "rol": "administrador"}
    token = crear_token(data)
    decoded = verificar_token(token)
    assert decoded["rol"] == "administrador"
    assert decoded["sub"] == "1"
