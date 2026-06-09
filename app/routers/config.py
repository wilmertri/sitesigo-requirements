# -*- coding: utf-8 -*-
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_super_admin
from app.database import get_db
from app.repositories.config_repository import ConfigRepository
from app.schemas.config_schemas import (
    CampoConfigCreate,
    CampoConfigResponse,
    EstadoConfigCreate,
    EstadoConfigResponse,
)
from app.services.dias_habiles_service import calcular_dias_habiles

import json

router = APIRouter(prefix="/proyectos", tags=["configuracion"])


@router.post("/{proyecto_id}/campos", status_code=201, response_model=CampoConfigResponse)
def crear_campo(
    proyecto_id: int,
    body: CampoConfigCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_super_admin),
):
    campo = ConfigRepository.crear_campo(db, proyecto_id, body)
    return CampoConfigResponse.from_orm(campo)


@router.get("/{proyecto_id}/campos", response_model=list[CampoConfigResponse])
def listar_campos(
    proyecto_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    campos = ConfigRepository.listar_campos(db, proyecto_id)
    return [CampoConfigResponse.from_orm(c) for c in campos]


@router.post("/{proyecto_id}/estados", status_code=201, response_model=EstadoConfigResponse)
def crear_estado(
    proyecto_id: int,
    body: EstadoConfigCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_super_admin),
):
    estado = ConfigRepository.crear_estado(db, proyecto_id, body)
    return EstadoConfigResponse.from_orm(estado)


@router.get("/{proyecto_id}/estados", response_model=list[EstadoConfigResponse])
def listar_estados(
    proyecto_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    estados = ConfigRepository.listar_estados(db, proyecto_id)
    return [EstadoConfigResponse.from_orm(e) for e in estados]


@router.get("/{proyecto_id}/dias-habiles")
def calcular_dias_habiles_endpoint(
    proyecto_id: int,
    fecha_inicio: date,
    fecha_final: date,
    _: dict = Depends(get_current_user),
):
    return {"dias_habiles": calcular_dias_habiles(fecha_inicio, fecha_final)}
