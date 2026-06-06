# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from app.schemas.requirement_schema import Prioridad, TipoRequerimiento

if TYPE_CHECKING:
    from app.models.history import CambioEstado


class RolUsuario(str, Enum):
    administrador = "administrador"
    funcionario = "funcionario"
    equipo_tecnico = "equipo_tecnico"


class EstadoRequerimiento(str, Enum):
    nuevo = "Nuevo"
    en_analisis = "En analisis"
    en_desarrollo = "En desarrollo"
    resuelto = "Resuelto"
    cerrado = "Cerrado"
    rechazado = "Rechazado"


@dataclass
class Requerimiento:
    id: int
    titulo: str
    descripcion: str
    tipo: TipoRequerimiento
    prioridad: Prioridad
    autor_id: int
    autor_rol: RolUsuario
    creado_en: datetime
    estado: EstadoRequerimiento = EstadoRequerimiento.nuevo
    autor_email: str = ""
    historial: list[CambioEstado] = field(default_factory=list)
