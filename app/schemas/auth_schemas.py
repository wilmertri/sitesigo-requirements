# -*- coding: utf-8 -*-
from pydantic import BaseModel


class RegistroBody(BaseModel):
    email: str
    password: str
    nombre: str
    rol: str = "funcionario"


class UsuarioResponse(BaseModel):
    id: int
    email: str
    rol: str
    nombre: str
    activo: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
