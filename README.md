# ReqFlow — Gestor de Requerimientos

![Tests](https://github.com/wilmertri/sitesigo-requirements/actions/workflows/tests.yml/badge.svg)

## API en Produccion

Base URL: https://sitesigo-requirements-production.up.railway.app

- Documentacion Swagger: https://sitesigo-requirements-production.up.railway.app/docs
- ReDoc: https://sitesigo-requirements-production.up.railway.app/redoc
- Health check: https://sitesigo-requirements-production.up.railway.app/health

Herramienta independiente para gestionar requerimientos
de cualquier proyecto de software, construida con un
pipeline TDD asistido por agentes de IA (Claude Code).

## Stack

- Python 3.13
- FastAPI
- SQLAlchemy + SQLite (dev) / PostgreSQL (prod)
- Pydantic v2
- pytest + behave (BDD)

## Pipeline de desarrollo

Este proyecto sigue el flujo:

Idea -> Spec formal -> Gherkin -> TDD -> Arquitectura -> Refactor

Cada regla de negocio tiene su escenario Gherkin
y sus tests antes de existir como codigo.

## Reglas de negocio implementadas

| ID    | Regla                                      | Tests      |
|-------|--------------------------------------------|------------|
| RN-01 | Campos obligatorios y valores validos      | 6          |
| RN-02 | Solo Admin cambia el estado                | 4          |
| RN-03 | Funcionario edita solo lo suyo en Nuevo    | 5          |
| RN-04 | Historial de cambios con actor y fecha     | 4          |
| RN-05 | Email best-effort al cambiar estado        | 4          |
| RN-06 | Prioridad solo Alta / Media / Baja         | (en RN-01) |
| RN-07 | Estados Cerrado y Rechazado son terminales | 3          |

Total: 50 tests — 0 fallos

## Actores

| Actor          | Permisos                                          |
|----------------|---------------------------------------------------|
| Administrador  | Gestion completa, unico que cambia estados        |
| Funcionario    | Crea y consulta, edita solo los suyos en Nuevo    |
| Equipo tecnico | Consulta y comenta                                |

## Ciclo de vida de un requerimiento

Nuevo -> En analisis -> En desarrollo -> Resuelto -> Cerrado
                                                  -> Rechazado

## Estructura del proyecto

app/
  models/       entidades de dominio
  schemas/      validacion Pydantic
  services/     logica de negocio
  routers/      endpoints FastAPI
tests/
  unit/         tests de schemas y services
  integration/  tests de endpoints
features/       escenarios Gherkin (behave)
agents/         prompts base de los agentes IA
specs/          especificacion formal
docs/decisions/ Architecture Decision Records

## Como correr los tests

# Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux

# Instalar dependencias
pip install -r requirements.txt

# Correr todos los tests
pytest tests/ -v

# Correr con cobertura
pytest tests/ -v --cov=app --cov-report=term-missing

## Decisiones de arquitectura

| ADR     | Decision                                        |
|---------|-------------------------------------------------|
| ADR-001 | Python + FastAPI como stack backend             |
| ADR-002 | Enums para valores de dominio cerrado           |
| ADR-003 | Orden de guardas en cambiar_estado              |
| ADR-004 | Resolucion de import circular entre modelos     |
| ADR-005 | Email como operacion best-effort                |

Ver detalles en docs/decisions/.

## Agentes de IA en el pipeline

Este proyecto usa Claude Code como agente TDD.
Los prompts base de cada agente estan en agents/.

Para iniciar una sesion con contexto completo:

Lee CLAUDE.md, agents/tdd_agent.md y
specs/spec_formal.md. Confirma que entendiste
y dime en que punto esta el proyecto.

## Roadmap

- [x] Schemas con validacion Pydantic
- [x] Modelos de dominio
- [x] Servicios con logica de negocio (RN-01 a RN-07)
- [x] Endpoints FastAPI
- [x] Autenticacion JWT con roles
- [x] Deploy en Railway (produccion)
- [x] PostgreSQL en produccion (Neon via Railway)
- [x] CI/CD automatico con GitHub Actions
- [x] Escenarios Gherkin ejecutables con behave
- [ ] Frontend Vue 3 + Vite

## Licencia

MIT
