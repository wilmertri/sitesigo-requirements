# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.requirement_db import CambioEstadoDB, RequerimientooDB
from app.schemas.requirement_schema import RequirementCreate


class RequirementRepository:
    @staticmethod
    def crear(
        db: Session,
        datos: RequirementCreate,
        autor_id: int,
        autor_rol: str,
        autor_email: str = "",
    ) -> RequerimientooDB:
        orm_req = RequerimientooDB(
            titulo=datos.titulo,
            descripcion=datos.descripcion,
            tipo=datos.tipo.value,
            prioridad=datos.prioridad.value,
            estado="Nuevo",
            autor_id=autor_id,
            autor_rol=autor_rol,
            autor_email=autor_email,
            creado_en=datetime.now(timezone.utc),
        )
        db.add(orm_req)
        db.commit()
        db.refresh(orm_req)
        return orm_req

    @staticmethod
    def obtener_por_id(db: Session, req_id: int) -> Optional[RequerimientooDB]:
        return db.query(RequerimientooDB).filter(RequerimientooDB.id == req_id).first()

    @staticmethod
    def listar(
        db: Session,
        estado: Optional[str] = None,
        tipo: Optional[str] = None,
        prioridad: Optional[str] = None,
    ) -> list[RequerimientooDB]:
        query = db.query(RequerimientooDB)
        if estado:
            query = query.filter(RequerimientooDB.estado == estado)
        if tipo:
            query = query.filter(RequerimientooDB.tipo == tipo)
        if prioridad:
            query = query.filter(RequerimientooDB.prioridad == prioridad)
        return query.all()

    @staticmethod
    def guardar_cambio_estado(
        db: Session,
        requerimiento_id: int,
        usuario_id: int,
        rol_usuario: str,
        estado_anterior: str,
        estado_nuevo: str,
    ) -> CambioEstadoDB:
        cambio = CambioEstadoDB(
            requerimiento_id=requerimiento_id,
            usuario_id=usuario_id,
            rol_usuario=rol_usuario,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            fecha=datetime.now(timezone.utc),
        )
        db.add(cambio)
        db.commit()
        db.refresh(cambio)
        return cambio

    @staticmethod
    def actualizar_estado(
        db: Session,
        requerimiento: RequerimientooDB,
        nuevo_estado: str,
    ) -> RequerimientooDB:
        requerimiento.estado = nuevo_estado
        db.commit()
        db.refresh(requerimiento)
        return requerimiento
