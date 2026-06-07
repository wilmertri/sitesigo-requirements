# -*- coding: utf-8 -*-
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.auth.jwt_handler import verificar_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    return verificar_token(token)


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("rol") != "administrador":
        raise HTTPException(status_code=403, detail="Se requiere rol de Administrador")
    return current_user
