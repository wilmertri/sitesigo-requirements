# -*- coding: utf-8 -*-
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import ValidationError

from app.models.requirement import EstadoRequerimiento, RolUsuario
from app.schemas.api_schemas import (
    CambiarEstadoBody,
    CrearRequirementBody,
    RequirementResponse,
)
from app.schemas.requirement_schema import RequirementCreate
from app.services.requirement_service import RequirementService

router = APIRouter(prefix="/requerimientos", tags=["requerimientos"])


@router.post("/", status_code=201, response_model=RequirementResponse)
def crear_requerimiento(body: CrearRequirementBody):
    try:
        datos = RequirementCreate(
            titulo=body.titulo,
            descripcion=body.descripcion,
            tipo=body.tipo,
            prioridad=body.prioridad,
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    try:
        rol = RolUsuario(body.autor_rol)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Rol invalido: {body.autor_rol!r}")

    req = RequirementService.crear(
        datos=datos,
        autor_id=body.autor_id,
        autor_rol=rol,
        autor_email=body.autor_email,
    )
    return RequirementResponse.from_requerimiento(req)


@router.get("/", response_model=list[RequirementResponse])
def listar_requerimientos(
    estado: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    prioridad: Optional[str] = Query(None),
):
    return []


@router.patch("/{req_id}/estado", response_model=RequirementResponse)
def cambiar_estado(req_id: int, body: CambiarEstadoBody):
    req = RequirementService.obtener_por_id(req_id)
    if req is None:
        raise HTTPException(status_code=404, detail="Requerimiento no encontrado")

    try:
        rol = RolUsuario(body.rol_usuario)
        estado = EstadoRequerimiento(body.nuevo_estado)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    try:
        req = RequirementService.cambiar_estado(
            requerimiento=req,
            nuevo_estado=estado,
            rol_usuario=rol,
            usuario_id=body.usuario_id,
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return RequirementResponse.from_requerimiento(req)
