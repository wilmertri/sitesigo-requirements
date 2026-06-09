# -*- coding: utf-8 -*-
import json
from typing import Optional

from sqlalchemy.orm import Session

from app.models.config_db import (
    ProyectoConfigCampoDB,
    ProyectoConfigEstadoDB,
    RequerimientoValorCampoDB,
)
from app.schemas.config_schemas import CampoConfigCreate, EstadoConfigCreate


class ConfigRepository:

    @staticmethod
    def crear_campo(
        db: Session,
        proyecto_id: int,
        datos: CampoConfigCreate,
    ) -> ProyectoConfigCampoDB:
        campo = ProyectoConfigCampoDB(
            proyecto_id=proyecto_id,
            nombre=datos.nombre,
            clave=datos.clave,
            tipo=datos.tipo.value,
            opciones=json.dumps(datos.opciones) if datos.opciones else None,
            obligatorio=datos.obligatorio,
            orden=datos.orden,
        )
        db.add(campo)
        db.commit()
        db.refresh(campo)
        return campo

    @staticmethod
    def listar_campos(db: Session, proyecto_id: int) -> list[ProyectoConfigCampoDB]:
        return (
            db.query(ProyectoConfigCampoDB)
            .filter(ProyectoConfigCampoDB.proyecto_id == proyecto_id)
            .order_by(ProyectoConfigCampoDB.orden)
            .all()
        )

    @staticmethod
    def crear_estado(
        db: Session,
        proyecto_id: int,
        datos: EstadoConfigCreate,
    ) -> ProyectoConfigEstadoDB:
        estado = ProyectoConfigEstadoDB(
            proyecto_id=proyecto_id,
            nombre=datos.nombre,
            color=datos.color,
            orden=datos.orden,
            es_terminal=datos.es_terminal,
        )
        db.add(estado)
        db.commit()
        db.refresh(estado)
        return estado

    @staticmethod
    def listar_estados(db: Session, proyecto_id: int) -> list[ProyectoConfigEstadoDB]:
        return (
            db.query(ProyectoConfigEstadoDB)
            .filter(ProyectoConfigEstadoDB.proyecto_id == proyecto_id)
            .order_by(ProyectoConfigEstadoDB.orden)
            .all()
        )

    @staticmethod
    def obtener_campo_por_clave(
        db: Session,
        proyecto_id: int,
        clave: str,
    ) -> Optional[ProyectoConfigCampoDB]:
        return (
            db.query(ProyectoConfigCampoDB)
            .filter(
                ProyectoConfigCampoDB.proyecto_id == proyecto_id,
                ProyectoConfigCampoDB.clave == clave,
            )
            .first()
        )

    @staticmethod
    def guardar_valor_campo(
        db: Session,
        requerimiento_id: int,
        campo_id: int,
        valor: Optional[str],
    ) -> RequerimientoValorCampoDB:
        valor_db = RequerimientoValorCampoDB(
            requerimiento_id=requerimiento_id,
            campo_id=campo_id,
            valor=str(valor) if valor is not None else None,
        )
        db.add(valor_db)
        db.commit()
        db.refresh(valor_db)
        return valor_db

    @staticmethod
    def obtener_estado_por_nombre(
        db: Session,
        proyecto_id: int,
        nombre: str,
    ) -> Optional[ProyectoConfigEstadoDB]:
        return (
            db.query(ProyectoConfigEstadoDB)
            .filter(
                ProyectoConfigEstadoDB.proyecto_id == proyecto_id,
                ProyectoConfigEstadoDB.nombre == nombre,
            )
            .first()
        )

    @staticmethod
    def actualizar_o_insertar_valor_campo(
        db: Session,
        requerimiento_id: int,
        campo_id: int,
        valor: Optional[str],
    ) -> RequerimientoValorCampoDB:
        existente = (
            db.query(RequerimientoValorCampoDB)
            .filter(
                RequerimientoValorCampoDB.requerimiento_id == requerimiento_id,
                RequerimientoValorCampoDB.campo_id == campo_id,
            )
            .first()
        )
        if existente:
            existente.valor = str(valor) if valor is not None else None
            db.commit()
            db.refresh(existente)
            return existente
        return ConfigRepository.guardar_valor_campo(db, requerimiento_id, campo_id, valor)

    @staticmethod
    def listar_valores_campo(
        db: Session,
        requerimiento_id: int,
    ) -> list[RequerimientoValorCampoDB]:
        return (
            db.query(RequerimientoValorCampoDB)
            .filter(RequerimientoValorCampoDB.requerimiento_id == requerimiento_id)
            .all()
        )
