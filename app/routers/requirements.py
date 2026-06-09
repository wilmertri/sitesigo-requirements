# -*- coding: utf-8 -*-
import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.requirement import EstadoRequerimiento, Requerimiento, RolUsuario
from app.models.requirement_db import RequerimientooDB
from app.repositories.config_repository import ConfigRepository
from app.repositories.requirement_repository import RequirementRepository
from app.schemas.api_schemas import (
    ActualizarValoresBody,
    ArchivarBody,
    CambiarEstadoBody,
    CambiarEstadoProyectoBody,
    CrearRequirementBody,
    EditarObservacionesBody,
    RequirementResponse,
)
from app.schemas.requirement_schema import Prioridad, RequirementCreate, TipoRequerimiento
from app.services.requirement_service import RequirementService

router = APIRouter(prefix="/requerimientos", tags=["requerimientos"])


def _orm_a_dominio(orm_req: RequerimientooDB) -> Requerimiento:
    return Requerimiento(
        id=orm_req.id,
        titulo=orm_req.titulo,
        descripcion=orm_req.descripcion,
        tipo=TipoRequerimiento(orm_req.tipo),
        prioridad=Prioridad(orm_req.prioridad),
        estado=EstadoRequerimiento(orm_req.estado),
        autor_id=orm_req.autor_id,
        autor_rol=RolUsuario(orm_req.autor_rol),
        autor_email=orm_req.autor_email,
        creado_en=orm_req.creado_en,
    )


def _proyecto_del_token(current_user: dict) -> int:
    proyecto_id = current_user.get("proyecto_id")
    if not proyecto_id:
        raise HTTPException(status_code=403, detail="Se requiere contexto de proyecto en el token")
    return proyecto_id


@router.post("", status_code=201, response_model=RequirementResponse)
@router.post("/", status_code=201, response_model=RequirementResponse)
def crear_requerimiento(
    body: CrearRequirementBody,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    proyecto_id = _proyecto_del_token(current_user)

    try:
        datos = RequirementCreate(
            titulo=body.titulo,
            descripcion=body.descripcion,
            tipo=body.tipo,
            prioridad=body.prioridad,
        )
    except ValidationError as e:
        # e.errors() puede contener ValueError en ctx que no es JSON-serializable
        raise HTTPException(status_code=422, detail=json.loads(e.json()))

    try:
        rol = RolUsuario(current_user["rol"])
    except ValueError:
        raise HTTPException(status_code=422, detail="Rol invalido en token")

    orm_req = RequirementRepository.crear(
        db=db,
        datos=datos,
        autor_id=int(current_user["sub"]),
        autor_rol=rol.value,
        autor_email=current_user.get("email", ""),
        proyecto_id=proyecto_id,
    )

    for clave, valor in body.valores_adicionales.items():
        campo = ConfigRepository.obtener_campo_por_clave(db, proyecto_id, clave)
        if campo is not None:
            ConfigRepository.guardar_valor_campo(db, orm_req.id, campo.id, valor)

    return RequirementResponse.from_orm_model(orm_req)


@router.get("", response_model=list[RequirementResponse])
@router.get("/", response_model=list[RequirementResponse])
def listar_requerimientos(
    estado: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    prioridad: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    rol = current_user.get("rol")
    proyecto_id_filtro = None if rol == "super_admin" else current_user.get("proyecto_id")
    autor_id_filtro = int(current_user["sub"]) if rol == "funcionario" else None
    lista = RequirementRepository.listar(
        db,
        estado=estado,
        tipo=tipo,
        prioridad=prioridad,
        proyecto_id=proyecto_id_filtro,
        autor_id=autor_id_filtro,
    )
    return [RequirementResponse.from_orm_model(r) for r in lista]


@router.get("/{req_id}")
def obtener_detalle_requerimiento(
    req_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    detalle = RequirementRepository.obtener_detalle(db, req_id)
    if detalle is None:
        raise HTTPException(status_code=404, detail="Requerimiento no encontrado")

    proyecto_id = current_user.get("proyecto_id")
    if proyecto_id is not None and detalle.get("proyecto_id") != proyecto_id:
        raise HTTPException(status_code=404, detail="Requerimiento no encontrado")

    return detalle


@router.patch("/{req_id}/estado", response_model=RequirementResponse)
def cambiar_estado(
    req_id: int,
    body: CambiarEstadoBody,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    orm_req = RequirementRepository.obtener_por_id(db, req_id)
    if orm_req is None:
        raise HTTPException(status_code=404, detail="Requerimiento no encontrado")

    proyecto_id = current_user.get("proyecto_id")
    if proyecto_id is not None and orm_req.proyecto_id != proyecto_id:
        raise HTTPException(status_code=404, detail="Requerimiento no encontrado")

    try:
        rol = RolUsuario(current_user["rol"])
        nuevo_estado = EstadoRequerimiento(body.nuevo_estado)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    estado_anterior = orm_req.estado
    req_domain = _orm_a_dominio(orm_req)

    try:
        RequirementService.cambiar_estado(
            requerimiento=req_domain,
            nuevo_estado=nuevo_estado,
            rol_usuario=rol,
            usuario_id=int(current_user["sub"]),
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    RequirementRepository.actualizar_estado(db, orm_req, nuevo_estado.value)
    RequirementRepository.guardar_cambio_estado(
        db,
        requerimiento_id=req_id,
        usuario_id=int(current_user["sub"]),
        rol_usuario=current_user["rol"],
        estado_anterior=estado_anterior,
        estado_nuevo=nuevo_estado.value,
    )
    return RequirementResponse.from_orm_model(orm_req)


@router.put("/{req_id}/valores")
def actualizar_valores(
    req_id: int,
    body: ActualizarValoresBody,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    orm_req = RequirementRepository.obtener_por_id(db, req_id)
    if orm_req is None:
        raise HTTPException(status_code=404, detail="Requerimiento no encontrado")

    usuario_id = int(current_user["sub"])
    rol = current_user["rol"]
    es_creador = orm_req.autor_id == usuario_id
    es_admin = rol in ("administrador", "super_admin")
    if not es_creador and not es_admin:
        raise HTTPException(status_code=403, detail="Sin permisos para actualizar valores")

    proyecto_id = orm_req.proyecto_id
    actualizado = 0
    for clave, valor in body.valores_adicionales.items():
        campo = ConfigRepository.obtener_campo_por_clave(db, proyecto_id, clave)
        if campo is not None:
            ConfigRepository.actualizar_o_insertar_valor_campo(db, req_id, campo.id, valor)
            actualizado += 1

    return {"actualizado": True, "campos_procesados": actualizado}


@router.patch("/{req_id}/estado-proyecto", response_model=RequirementResponse)
def cambiar_estado_proyecto(
    req_id: int,
    body: CambiarEstadoProyectoBody,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    orm_req = RequirementRepository.obtener_por_id(db, req_id)
    if orm_req is None:
        raise HTTPException(status_code=404, detail="Requerimiento no encontrado")

    if current_user["rol"] not in ("administrador", "super_admin"):
        raise HTTPException(status_code=403, detail="Solo el Administrador puede cambiar el estado del proyecto")

    estado = ConfigRepository.obtener_estado_por_nombre(
        db, orm_req.proyecto_id, body.estado_proyecto
    )
    if estado is None:
        raise HTTPException(
            status_code=422,
            detail=f"El estado '{body.estado_proyecto}' no esta configurado en este proyecto",
        )

    estado_anterior = orm_req.estado_proyecto or ""
    RequirementRepository.actualizar_estado_proyecto(db, orm_req, body.estado_proyecto)
    RequirementRepository.guardar_cambio_estado(
        db,
        requerimiento_id=req_id,
        usuario_id=int(current_user["sub"]),
        rol_usuario=current_user["rol"],
        estado_anterior=estado_anterior,
        estado_nuevo=body.estado_proyecto,
    )
    return RequirementResponse.from_orm_model(orm_req)


@router.patch("/{req_id}/observaciones")
def editar_observaciones(
    req_id: int,
    body: EditarObservacionesBody,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    orm_req = RequirementRepository.obtener_por_id(db, req_id)
    if orm_req is None:
        raise HTTPException(status_code=404, detail="Requerimiento no encontrado")

    if orm_req.autor_id != int(current_user["sub"]):
        raise HTTPException(status_code=403, detail="Solo el creador puede editar las observaciones")

    _ESTADOS_TERMINALES = {"Cerrado", "Rechazado"}
    if orm_req.estado in _ESTADOS_TERMINALES:
        raise HTTPException(
            status_code=422,
            detail=f"No se pueden editar observaciones en estado {orm_req.estado}",
        )

    campo = ConfigRepository.obtener_campo_por_clave(db, orm_req.proyecto_id, "observaciones")
    if campo is None:
        raise HTTPException(
            status_code=422,
            detail="El campo 'observaciones' no esta configurado en este proyecto",
        )

    ConfigRepository.actualizar_o_insertar_valor_campo(db, req_id, campo.id, body.observaciones)
    RequirementRepository.guardar_cambio_estado(
        db,
        requerimiento_id=req_id,
        usuario_id=int(current_user["sub"]),
        rol_usuario=current_user["rol"],
        estado_anterior=orm_req.estado,
        estado_nuevo="Observaciones actualizadas",
    )
    return {"actualizado": True}


@router.delete("/{req_id}", response_model=RequirementResponse)
def archivar_requerimiento(
    req_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    orm_req = RequirementRepository.obtener_por_id(db, req_id)
    if orm_req is None:
        raise HTTPException(status_code=404, detail="Requerimiento no encontrado")

    proyecto_id = current_user.get("proyecto_id")
    if proyecto_id is not None and orm_req.proyecto_id != proyecto_id:
        raise HTTPException(status_code=404, detail="Requerimiento no encontrado")

    try:
        orm_req = RequirementRepository.archivar(
            db, req_id, int(current_user["sub"]), current_user["rol"]
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return RequirementResponse.from_orm_model(orm_req)
