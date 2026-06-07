# -*- coding: utf-8 -*-
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user_db import UsuarioDB


class UserRepository:
    @staticmethod
    def crear(
        db: Session,
        email: str,
        hashed_password: str,
        rol: str,
        nombre: str,
    ) -> UsuarioDB:
        usuario = UsuarioDB(
            email=email,
            hashed_password=hashed_password,
            rol=rol,
            nombre=nombre,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    @staticmethod
    def obtener_por_email(db: Session, email: str) -> Optional[UsuarioDB]:
        return db.query(UsuarioDB).filter(UsuarioDB.email == email).first()

    @staticmethod
    def obtener_por_id(db: Session, user_id: int) -> Optional[UsuarioDB]:
        return db.query(UsuarioDB).filter(UsuarioDB.id == user_id).first()
