# -*- coding: utf-8 -*-
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import config_db, project_db, requirement_db, user_db  # noqa: F401
from app.models.config_db import ProyectoConfigCampoDB
from app.models.project_db import ProyectoDB


@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def proyecto_sitesigo(db) -> int:
    from app.auth.password_handler import hashear_password
    from app.models.user_db import UsuarioDB

    owner = UsuarioDB(
        email="sa@test.com",
        hashed_password=hashear_password("sa123"),
        rol="super_admin",
        nombre="SA",
    )
    db.add(owner)
    db.commit()
    db.refresh(owner)

    proyecto = ProyectoDB(nombre="SITESIGO", creado_por_id=owner.id)
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)
    return proyecto.id


def _ejecutar_seed(db, proyecto_id: int):
    from scripts.seed_sitesigo import campos_ya_existen, crear_campos
    if not campos_ya_existen(db, proyecto_id):
        crear_campos(db, proyecto_id)


def test_seed_crea_seis_campos(db, proyecto_sitesigo):
    _ejecutar_seed(db, proyecto_sitesigo)

    campos = db.query(ProyectoConfigCampoDB).filter(
        ProyectoConfigCampoDB.proyecto_id == proyecto_sitesigo
    ).order_by(ProyectoConfigCampoDB.orden).all()

    assert len(campos) == 6


def test_seed_crea_campo_calculado(db, proyecto_sitesigo):
    _ejecutar_seed(db, proyecto_sitesigo)

    campo = db.query(ProyectoConfigCampoDB).filter(
        ProyectoConfigCampoDB.clave == "dias_habiles",
        ProyectoConfigCampoDB.proyecto_id == proyecto_sitesigo,
    ).first()

    assert campo is not None
    assert campo.tipo == "calculado"


def test_seed_crea_campo_lista_con_opciones(db, proyecto_sitesigo):
    _ejecutar_seed(db, proyecto_sitesigo)

    campo = db.query(ProyectoConfigCampoDB).filter(
        ProyectoConfigCampoDB.clave == "proceso",
        ProyectoConfigCampoDB.proyecto_id == proyecto_sitesigo,
    ).first()

    assert campo is not None
    assert "Seguimiento Fisico" in campo.opciones


def test_seed_es_idempotente(db, proyecto_sitesigo):
    _ejecutar_seed(db, proyecto_sitesigo)
    _ejecutar_seed(db, proyecto_sitesigo)  # segunda vez no duplica

    count = db.query(ProyectoConfigCampoDB).filter(
        ProyectoConfigCampoDB.proyecto_id == proyecto_sitesigo
    ).count()

    assert count == 6
