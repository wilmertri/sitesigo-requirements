# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from datetime import datetime

from app.models.requirement import EstadoRequerimiento, RolUsuario


@dataclass
class CambioEstado:
    requerimiento_id: int
    usuario_id: int
    rol_usuario: RolUsuario
    estado_anterior: EstadoRequerimiento
    estado_nuevo: EstadoRequerimiento
    fecha: datetime = field(default_factory=datetime.now)
