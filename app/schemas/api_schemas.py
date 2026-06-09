# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import BaseModel

ValorAdicional = str | int | float

from app.schemas.requirement_schema import Prioridad, TipoRequerimiento


class CrearRequirementBody(BaseModel):
    titulo: str
    descripcion: str
    tipo: TipoRequerimiento
    prioridad: Prioridad
    valores_adicionales: dict[str, ValorAdicional] = {}


class ActualizarValoresBody(BaseModel):
    valores_adicionales: dict[str, ValorAdicional] = {}


class CambiarEstadoBody(BaseModel):
    nuevo_estado: str


class CambiarEstadoProyectoBody(BaseModel):
    estado_proyecto: str


class EditarObservacionesBody(BaseModel):
    observaciones: str


class ArchivarBody(BaseModel):
    pass


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
    proyecto_id: int | None = None
    estado_proyecto: str | None = None

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
            proyecto_id=getattr(req, "proyecto_id", None),
            estado_proyecto=getattr(req, "estado_proyecto", None),
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
            proyecto_id=getattr(req, "proyecto_id", None),
            estado_proyecto=getattr(req, "estado_proyecto", None),
        )
