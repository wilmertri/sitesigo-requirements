# -*- coding: utf-8 -*-
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_super_admin
from app.auth.password_handler import hashear_password
from app.database import get_db
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.services.project_service import ProjectService

router = APIRouter(prefix="/proyectos", tags=["proyectos"])


class CrearProyectoBody(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class AgregarUsuarioBody(BaseModel):
    email: str
    rol: str
    nombre: Optional[str] = None
    password: Optional[str] = None


@router.post("", status_code=201)
@router.post("/", status_code=201)
def crear_proyecto(
    body: CrearProyectoBody,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    proyecto = ProjectRepository.crear(
        db,
        nombre=body.nombre,
        descripcion=body.descripcion,
        creado_por_id=int(current_user["sub"]),
    )
    return {
        "id": proyecto.id,
        "nombre": proyecto.nombre,
        "descripcion": proyecto.descripcion,
        "activo": proyecto.activo,
    }


@router.get("", response_model=list)
@router.get("/", response_model=list)
def listar_proyectos(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    rol = current_user.get("rol")
    if rol == "super_admin":
        proyectos = ProjectRepository.listar(db)
    else:
        proyecto_id = current_user.get("proyecto_id")
        if not proyecto_id:
            return []
        proyecto = ProjectRepository.obtener_por_id(db, proyecto_id)
        proyectos = [proyecto] if proyecto else []
    return [
        {"id": p.id, "nombre": p.nombre, "descripcion": p.descripcion, "activo": p.activo}
        for p in proyectos
    ]


@router.get("/{proyecto_id}")
def obtener_proyecto(
    proyecto_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    proyecto = ProjectRepository.obtener_por_id(db, proyecto_id)
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return {
        "id": proyecto.id,
        "nombre": proyecto.nombre,
        "descripcion": proyecto.descripcion,
        "activo": proyecto.activo,
    }


@router.post("/{proyecto_id}/usuarios", status_code=201)
def agregar_usuario_a_proyecto(
    proyecto_id: int,
    body: AgregarUsuarioBody,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    rol_actual = current_user.get("rol")
    proyecto_actual = current_user.get("proyecto_id")

    if not ProjectService.puede_gestionar_usuarios(rol_actual):
        raise HTTPException(status_code=403, detail="Sin permisos para gestionar usuarios")

    if rol_actual != "super_admin" and proyecto_actual != proyecto_id:
        raise HTTPException(status_code=403, detail="Solo puede gestionar usuarios de su proyecto")

    proyecto = ProjectRepository.obtener_por_id(db, proyecto_id)
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    usuario = UserRepository.obtener_por_email(db, body.email)
    if not usuario:
        password = body.password or "temporal123"
        usuario = UserRepository.crear(
            db,
            email=body.email,
            hashed_password=hashear_password(password),
            rol=body.rol,
            nombre=body.nombre or body.email.split("@")[0],
        )

    if ProjectRepository.obtener_rol_usuario(db, proyecto_id, usuario.id):
        raise HTTPException(status_code=400, detail="El usuario ya pertenece al proyecto")

    membresia = ProjectRepository.agregar_usuario(db, proyecto_id, usuario.id, body.rol)

    try:
        _enviar_bienvenida(body.email, proyecto.nombre)
    except Exception:
        pass

    return {
        "usuario_id": usuario.id,
        "email": usuario.email,
        "proyecto_id": proyecto_id,
        "rol": membresia.rol,
    }


@router.get("/{proyecto_id}/usuarios")
def obtener_usuarios_proyecto(
    proyecto_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    rol_actual = current_user.get("rol")
    proyecto_actual = current_user.get("proyecto_id")

    if rol_actual not in ("super_admin", "administrador"):
        raise HTTPException(status_code=403, detail="Sin permisos")

    if rol_actual != "super_admin" and proyecto_actual != proyecto_id:
        raise HTTPException(status_code=403, detail="Solo puede ver usuarios de su proyecto")

    proyecto = ProjectRepository.obtener_por_id(db, proyecto_id)
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    return ProjectRepository.obtener_usuarios(db, proyecto_id)


def _enviar_bienvenida(email: str, nombre_proyecto: str) -> None:
    pass  # implementacion real con Resend va despues
