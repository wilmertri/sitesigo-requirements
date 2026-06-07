# ReqFlow

## Que es este proyecto
Herramienta SaaS independiente para gestionar
requerimientos de cualquier proyecto de software.
Stack: Python 3.13, FastAPI, SQLAlchemy, 
Pydantic v2, pytest, behave.

## Actores
- Administrador: gestion completa de 
  requerimientos, unico que cambia estados
- Funcionario: crea requerimientos,
  ve todos en modo lectura, edita solo los suyos 
  en estado Nuevo
- Equipo tecnico: ve todos, agrega comentarios,
  no cambia estado ni prioridad

## Reglas de negocio
- RN-01: titulo, descripcion, tipo y prioridad 
  son obligatorios para guardar un requerimiento
- RN-02: solo el Administrador puede cambiar 
  el estado de un requerimiento
- RN-03: un Funcionario solo puede editar un 
  requerimiento si esta en estado Nuevo
- RN-04: cada cambio de estado queda registrado 
  con actor, fecha/hora y estado anterior
- RN-05: al cambiar estado se envia email al 
  creador si es Funcionario
- RN-06: prioridad solo puede ser Alta, Media o Baja
- RN-07: estados Cerrado y Rechazado son terminales,
  no pueden cambiar

## Ciclo de vida de estados
Nuevo -> En analisis -> En desarrollo -> Resuelto -> Cerrado
Desde cualquier estado -> Rechazado (solo Administrador)

## Convenciones de codigo
- Siempre UTF-8 en todos los archivos
- TDD: tests antes que codigo, sin excepciones
- Un test por cada regla de negocio
- Validators en schemas/, logica en services/
- Nunca logica de negocio en routers/
- Enums para valores de dominio cerrado
- Nombres en español para el dominio de negocio,
  ingles para estructuras tecnicas

## Estructura del proyecto
app/schemas/       validacion Pydantic (RN-01, RN-06)
app/services/      logica de negocio (RN-02 a RN-07)
app/models/        entidades SQLAlchemy
app/routers/       endpoints FastAPI
tests/unit/        tests de schemas y services
tests/integration/ tests de endpoints completos
features/          escenarios Gherkin (behave)
agents/            prompts base de cada agente IA
specs/             especificacion formal del sistema
docs/decisions/    Architecture Decision Records (ADRs)

## Como trabajar en este proyecto
1. Leer la regla de negocio en specs/spec_formal.md
2. Escribir el escenario Gherkin en features/
3. Escribir el test que falla (Red)
4. Escribir el codigo minimo que pasa (Green)
5. Refactorizar sin romper tests (Refactor)
6. Nunca saltarse el paso 3

## Agentes disponibles

### Como invocar un agente
Al inicio de cada sesion di:
"Lee CLAUDE.md, agents/tdd_agent.md y 
specs/spec_formal.md. Confirma que entendiste 
y dime en que punto esta el proyecto."

### Agente 1 - Analista (agents/analyst_agent.md)
Usar cuando:
- Llega un requerimiento nuevo o cambio de negocio
- Hay ambiguedades antes de escribir codigo
- Se necesita definir actores o flujos nuevos
Invocar con:
"Lee agents/analyst_agent.md y actua segun ese rol
para analizar: [descripcion del requerimiento]"

### Agente 2 - TDD (agents/tdd_agent.md)
Usar cuando:
- Se va a implementar una regla de negocio
- Se necesita escribir tests antes que codigo
- Se va a hacer un refactor
Invocar con:
"Lee agents/tdd_agent.md y actua segun ese rol
para implementar: [nombre de la regla RN-XX]"

### Especificacion y decisiones
- specs/spec_formal.md → consultar antes de 
  implementar cualquier regla de negocio
- docs/decisions/ADR-*.md → consultar cuando
  surja una duda arquitectonica

## Estado actual del proyecto

### Completado
- Estructura de carpetas y archivos base
- app/schemas/requirement_schema.py
  Enums Prioridad y TipoRequerimiento
  RequirementCreate con validators
  model_config extra=forbid
- tests/unit/test_requirement_schema.py
  6 tests en verde (RN-01 y RN-06 cubiertos)
- app/models/requirement.py
  Enums RolUsuario y EstadoRequerimiento
  Dataclass Requerimiento
- app/services/requirement_service.py
  RequirementService.cambiar_estado()
  RN-02 y RN-07 implementadas
- tests/unit/test_editar_requerimiento.py
  5 tests en verde (RN-03 cubierto)
- app/services/requirement_service.py actualizado
  metodo editar() con 3 guardas
  metodo privado _verificar_no_terminal()
  extrae logica compartida entre cambiar_estado y editar
- app/models/history.py
  Dataclass CambioEstado (RN-04)
- app/models/requirement.py actualizado
  campo historial con TYPE_CHECKING (ADR-004)
- tests/unit/test_historial.py
  4 tests en verde (RN-04 cubierto)
- app/services/requirement_service.py actualizado
  cambiar_estado() registra CambioEstado en historial
  firma extendida con usuario_id
- app/services/notification_service.py
  NotificationService.enviar_cambio_estado() (RN-05)
- app/models/requirement.py actualizado
  campo autor_email con default vacio
- tests/unit/test_notificaciones.py
  4 tests en verde (RN-05 cubierto)
- app/services/requirement_service.py actualizado
  notificacion best-effort con try/except (ADR-005)
  Total: 26 tests en verde
- Documentacion base
  CLAUDE.md, agents/, specs/, docs/decisions/
  ADR-001 (stack Python+FastAPI)
  ADR-002 (Enums para dominio cerrado)
  ADR-003 (Orden de guardas en cambiar_estado)
  ADR-004 (Resolucion de import circular entre modelos)
  ADR-005 (Email como operacion best-effort)

- Endpoints FastAPI (app/routers/requirements.py)
  POST /requerimientos (crear)
  GET /requerimientos (listar con filtros opcionales)
  PATCH /requerimientos/{id}/estado (cambiar estado)
  app/schemas/api_schemas.py: modelos HTTP desacoplados
  tests/integration/conftest.py + test_endpoints.py
  5 tests de integracion nuevos
  Total: 31 tests en verde (26 unit + 5 integration)

- Persistencia SQLAlchemy
  app/database.py: engine SQLite + SessionLocal + get_db
  app/models/requirement_db.py: RequerimientooDB y CambioEstadoDB
  app/repositories/requirement_repository.py: crear, listar,
    obtener_por_id, actualizar_estado, guardar_cambio_estado
  app/schemas/api_schemas.py: from_orm_model() para ORM objects
  GET /requerimientos con filtros reales (estado, tipo, prioridad)
  tests/integration/conftest.py: StaticPool para SQLite in-memory
  tests/integration/test_repository.py: 4 tests nuevos
  ADR-006 (StaticPool en tests de integracion)
  Total: 35 tests en verde

- Borrado logico con estado Archivado
  RN-08: solo Admin puede archivar
  RN-09: archivado queda registrado en historial
  RN-10: archivados excluidos del listado normal por defecto
  EstadoRequerimiento.archivado como estado terminal
  RequirementService.archivar() con duck typing ORM→service
  RequirementRepository.archivar(): persiste + historial
  RequirementRepository.listar(): excluye Archivados por defecto
  DELETE /requerimientos/{id} (200/403/404/422)
  ArchivarBody en api_schemas.py
  tests/unit/test_archivar.py: 4 tests nuevos
  test_repository.py: 1 test nuevo
  ADR-006: StaticPool para tests de integracion
  Total: 40 tests en verde

- Autenticacion JWT con roles
  app/auth/jwt_handler.py: crear_token, verificar_token (python-jose)
  app/auth/password_handler.py: hashear/verificar con bcrypt directo
  app/auth/dependencies.py: get_current_user, require_admin
  app/models/user_db.py: UsuarioDB SQLAlchemy (tabla usuarios)
  app/repositories/user_repository.py: crear, obtener_por_email/id
  app/schemas/auth_schemas.py: RegistroBody, TokenResponse, UsuarioResponse
  app/routers/auth.py: POST /auth/registro, POST /auth/token, GET /auth/me
  app/routers/requirements.py: Depends(get_current_user) en todos los endpoints
  api_schemas.py: eliminados rol/usuario_id del body (viajan en token)
  conftest.py: fixtures admin_token y funcionario_token
  tests/unit/test_auth.py: 5 tests nuevos
  tests/integration/test_auth_endpoints.py: 5 tests nuevos
  Total: 50 tests en verde

- Gherkin ejecutable con behave
  features/environment.py: setup con SQLite in-memory y StaticPool
  features/requirements.feature: 6 escenarios (RN-01, RN-02, RN-07, RN-08)
  features/steps/requirements_steps.py: 33 steps con re matcher
  6 escenarios en verde
  ADR-007: step matcher regex para strings vacios
  ADR-008: serializacion Pydantic v2 con json.loads(e.json())
  Total: 50 tests pytest + 6 escenarios behave

## Endpoints implementados y funcionando
- POST   /auth/registro               (registro de usuario)
- POST   /auth/token                  (login OAuth2, devuelve JWT)
- GET    /auth/me                     (datos del usuario autenticado)
- POST   /requerimientos/             (crear, requiere JWT)
- GET    /requerimientos/             (listar con filtros, publico)
- PATCH  /requerimientos/{id}/estado  (cambiar estado, requiere JWT Admin)
- DELETE /requerimientos/{id}         (archivar, requiere JWT Admin)

- Docker y docker-compose
  Dockerfile: python:3.13-slim con gcc + libpq-dev
  docker-compose.yml: api + PostgreSQL 16-alpine
  .dockerignore, .env.example
  Build verificado, 50 tests en verde dentro del contenedor

### Pendiente - siguiente ciclo TDD
- Frontend (Vue 3 + Vite)