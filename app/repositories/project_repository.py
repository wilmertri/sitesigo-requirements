# -*- coding: utf-8 -*-
from typing import Optional

from sqlalchemy.orm import Session

from app.models.project_db import ProyectoDB, UsuarioProyectoDB


class ProjectRepository:
    @staticmethod
    def crear(
        db: Session,
        nombre: str,
        descripcion: Optional[str],
        creado_por_id: int,
    ) -> ProyectoDB:
        proyecto = ProyectoDB(
            nombre=nombre,
            descripcion=descripcion,
            activo=True,
            creado_por_id=creado_por_id,
        )
        db.add(proyecto)
        db.commit()
        db.refresh(proyecto)
        return proyecto

    @staticmethod
    def obtener_por_id(db: Session, proyecto_id: int) -> Optional[ProyectoDB]:
        return db.query(ProyectoDB).filter(ProyectoDB.id == proyecto_id).first()

    @staticmethod
    def listar(db: Session) -> list[ProyectoDB]:
        return db.query(ProyectoDB).filter(ProyectoDB.activo == True).all()  # noqa: E712

    @staticmethod
    def agregar_usuario(
        db: Session,
        proyecto_id: int,
        usuario_id: int,
        rol: str,
    ) -> UsuarioProyectoDB:
        membresia = UsuarioProyectoDB(
            usuario_id=usuario_id,
            proyecto_id=proyecto_id,
            rol=rol,
            activo=True,
        )
        db.add(membresia)
        db.commit()
        db.refresh(membresia)
        return membresia

    @staticmethod
    def obtener_usuarios(db: Session, proyecto_id: int) -> list[UsuarioProyectoDB]:
        return (
            db.query(UsuarioProyectoDB)
            .filter(
                UsuarioProyectoDB.proyecto_id == proyecto_id,
                UsuarioProyectoDB.activo == True,  # noqa: E712
            )
            .all()
        )

    @staticmethod
    def obtener_rol_usuario(
        db: Session, proyecto_id: int, usuario_id: int
    ) -> Optional[str]:
        membresia = (
            db.query(UsuarioProyectoDB)
            .filter(
                UsuarioProyectoDB.proyecto_id == proyecto_id,
                UsuarioProyectoDB.usuario_id == usuario_id,
                UsuarioProyectoDB.activo == True,  # noqa: E712
            )
            .first()
        )
        return membresia.rol if membresia else None
