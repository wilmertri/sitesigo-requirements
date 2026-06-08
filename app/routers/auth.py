# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, oauth2_scheme_optional
from app.auth.jwt_handler import crear_token, verificar_token
from app.auth.password_handler import hashear_password, verificar_password
from app.database import get_db
from app.models.project_db import UsuarioProyectoDB
from app.models.user_db import UsuarioDB
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schemas import RegistroBody, TokenResponse, UsuarioResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registro", status_code=201, response_model=UsuarioResponse)
def registro(
    body: RegistroBody,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme_optional),
):
    # Bootstrap: first user is allowed without auth
    user_count = db.query(UsuarioDB).count()
    if user_count > 0:
        if not token:
            raise HTTPException(status_code=401, detail="Se requiere autenticacion")
        current_user = verificar_token(token)
        if current_user.get("rol") not in ("administrador", "super_admin"):
            raise HTTPException(status_code=403, detail="Sin permisos para registrar usuarios")

    if UserRepository.obtener_por_email(db, body.email):
        raise HTTPException(status_code=400, detail="El email ya esta registrado")

    usuario = UserRepository.crear(
        db=db,
        email=body.email,
        hashed_password=hashear_password(body.password),
        rol=body.rol,
        nombre=body.nombre,
    )
    return UsuarioResponse(
        id=usuario.id,
        email=usuario.email,
        rol=usuario.rol,
        nombre=usuario.nombre,
        activo=usuario.activo,
    )


@router.post("/token", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = UserRepository.obtener_por_email(db, form.username)
    if not usuario or not verificar_password(form.password, usuario.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    membresia = (
        db.query(UsuarioProyectoDB)
        .filter(
            UsuarioProyectoDB.usuario_id == usuario.id,
            UsuarioProyectoDB.activo == True,  # noqa: E712
        )
        .first()
    )
    proyecto_id = membresia.proyecto_id if membresia else None
    rol = membresia.rol if membresia else usuario.rol

    token = crear_token({
        "sub": str(usuario.id),
        "email": usuario.email,
        "rol": rol,
        "nombre": usuario.nombre,
        "proyecto_id": proyecto_id,
    })
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user
