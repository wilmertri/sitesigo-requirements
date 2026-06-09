# -*- coding: utf-8 -*-
import json
import re
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class TipoCampo(str, Enum):
    texto = "texto"
    fecha = "fecha"
    numero = "numero"
    lista = "lista"
    calculado = "calculado"


class CampoConfigCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str
    clave: str
    tipo: TipoCampo
    opciones: list[str] = []
    obligatorio: bool = False
    orden: int = 0

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El nombre del campo es obligatorio")
        return v.strip()

    @field_validator("clave")
    @classmethod
    def clave_no_vacia(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("La clave del campo es obligatoria")
        return v.strip()

    @field_validator("opciones")
    @classmethod
    def lista_requiere_opciones(cls, v: list[str], info) -> list[str]:
        tipo = info.data.get("tipo")
        if tipo == TipoCampo.lista and not v:
            raise ValueError("Un campo de tipo lista debe tener al menos una opcion")
        return v


_COLOR_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


class EstadoConfigCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str
    color: str
    es_terminal: bool = False
    orden: int = 0

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El nombre del estado es obligatorio")
        return v.strip()

    @field_validator("color")
    @classmethod
    def color_hex_valido(cls, v: str) -> str:
        if not _COLOR_HEX.match(v):
            raise ValueError("El color debe ser un codigo hex valido (#rrggbb)")
        return v


class CampoConfigResponse(BaseModel):
    id: int
    proyecto_id: int
    nombre: str
    clave: str
    tipo: str
    opciones: list[str]
    obligatorio: bool
    orden: int

    @classmethod
    def from_orm(cls, obj) -> "CampoConfigResponse":
        return cls(
            id=obj.id,
            proyecto_id=obj.proyecto_id,
            nombre=obj.nombre,
            clave=obj.clave,
            tipo=obj.tipo,
            opciones=json.loads(obj.opciones) if obj.opciones else [],
            obligatorio=obj.obligatorio or False,
            orden=obj.orden or 0,
        )


class EstadoConfigResponse(BaseModel):
    id: int
    proyecto_id: int
    nombre: str
    color: str
    orden: int
    es_terminal: bool

    @classmethod
    def from_orm(cls, obj) -> "EstadoConfigResponse":
        return cls(
            id=obj.id,
            proyecto_id=obj.proyecto_id,
            nombre=obj.nombre,
            color=obj.color,
            orden=obj.orden or 0,
            es_terminal=obj.es_terminal or False,
        )
