# -*- coding: utf-8 -*-
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.requirement_db import CambioEstadoDB, RequerimientooDB
from app.schemas.requirement_schema import RequirementCreate
from app.services.requirement_service import RequirementService


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
        else:
            query = query.filter(RequerimientooDB.estado != "Archivado")
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
    def archivar(
        db: Session,
        requerimiento_id: int,
        usuario_id: int,
        rol_usuario: str,
    ) -> Optional[RequerimientooDB]:
        orm_req = RequirementRepository.obtener_por_id(db, requerimiento_id)
        if orm_req is None:
            return None
        estado_anterior = orm_req.estado
        RequirementService.archivar(orm_req, rol_usuario)
        db.commit()
        db.refresh(orm_req)
        RequirementRepository.guardar_cambio_estado(
            db,
            requerimiento_id=requerimiento_id,
            usuario_id=usuario_id,
            rol_usuario=rol_usuario,
            estado_anterior=estado_anterior,
            estado_nuevo="Archivado",
        )
        return orm_req

    @staticmethod
    def obtener_detalle(db: Session, req_id: int) -> dict | None:
        orm_req = db.query(RequerimientooDB).filter(RequerimientooDB.id == req_id).first()
        if orm_req is None:
            return None
        historial = (
            db.query(CambioEstadoDB)
            .filter(CambioEstadoDB.requerimiento_id == req_id)
            .order_by(CambioEstadoDB.fecha.asc())
            .all()
        )
        return {
            "id": orm_req.id,
            "titulo": orm_req.titulo,
            "descripcion": orm_req.descripcion,
            "tipo": orm_req.tipo,
            "prioridad": orm_req.prioridad,
            "estado": orm_req.estado,
            "autor_id": orm_req.autor_id,
            "autor_rol": orm_req.autor_rol,
            "autor_email": orm_req.autor_email,
            "creado_en": orm_req.creado_en,
            "historial": [
                {
                    "id": c.id,
                    "usuario_id": c.usuario_id,
                    "rol_usuario": c.rol_usuario,
                    "estado_anterior": c.estado_anterior,
                    "estado_nuevo": c.estado_nuevo,
                    "fecha": c.fecha,
                }
                for c in historial
            ],
        }

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
