# -*- coding: utf-8 -*-
from enum import Enum
from pydantic import BaseModel, ConfigDict, field_validator


def _validar_campo_no_vacio(valor: str, mensaje: str) -> str:
    if not valor or not valor.strip():
        raise ValueError(mensaje)
    return valor.strip()


class Prioridad(str, Enum):
    alta = "Alta"
    media = "Media"
    baja = "Baja"


class TipoRequerimiento(str, Enum):
    bug = "Bug"
    nueva_funcionalidad = "Nueva funcionalidad"
    cambio_en_modulo = "Cambio en modulo"
    mejora_ux_rendimiento = "Mejora UX/rendimiento"


class RequirementCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    titulo: str
    descripcion: str
    tipo: TipoRequerimiento
    prioridad: Prioridad

    @field_validator("titulo")
    @classmethod
    def titulo_no_vacio(cls, v: str) -> str:
        return _validar_campo_no_vacio(v, "El titulo es obligatorio")

    @field_validator("descripcion")
    @classmethod
    def descripcion_no_vacia(cls, v: str) -> str:
        return _validar_campo_no_vacio(v, "La descripcion es obligatoria")