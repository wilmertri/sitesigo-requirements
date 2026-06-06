# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import BaseModel

from app.schemas.requirement_schema import Prioridad, TipoRequerimiento


class CrearRequirementBody(BaseModel):
    titulo: str
    descripcion: str
    tipo: TipoRequerimiento
    prioridad: Prioridad
    autor_id: int
    autor_rol: str
    autor_email: str = ""


class CambiarEstadoBody(BaseModel):
    nuevo_estado: str
    usuario_id: int
    rol_usuario: str


class ArchivarBody(BaseModel):
    usuario_id: int
    rol_usuario: str


class RequirementResponse(BaseModel):
    id: int
    titulo: str
    descripcion: str
    tipo: str
    prioridad: str
    estado: str
    autor_id: int
    autor_rol: str
    autor_email: str
    creado_en: datetime

    @classmethod
    def from_requerimiento(cls, req) -> "RequirementResponse":
        return cls(
            id=req.id,
            titulo=req.titulo,
            descripcion=req.descripcion,
            tipo=req.tipo.value,
            prioridad=req.prioridad.value,
            estado=req.estado.value,
            autor_id=req.autor_id,
            autor_rol=req.autor_rol.value,
            autor_email=req.autor_email,
            creado_en=req.creado_en,
        )

    @classmethod
    def from_orm_model(cls, req) -> "RequirementResponse":
        return cls(
            id=req.id,
            titulo=req.titulo,
            descripcion=req.descripcion,
            tipo=req.tipo,
            prioridad=req.prioridad,
            estado=req.estado,
            autor_id=req.autor_id,
            autor_rol=req.autor_rol,
            autor_email=req.autor_email,
            creado_en=req.creado_en,
        )
