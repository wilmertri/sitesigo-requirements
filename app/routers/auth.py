# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.jwt_handler import crear_token
from app.auth.password_handler import hashear_password, verificar_password
from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schemas import RegistroBody, TokenResponse, UsuarioResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registro", status_code=201, response_model=UsuarioResponse)
def registro(body: RegistroBody, db: Session = Depends(get_db)):
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

    token = crear_token({
        "sub": str(usuario.id),
        "email": usuario.email,
        "rol": usuario.rol,
        "nombre": usuario.nombre,
    })
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user
