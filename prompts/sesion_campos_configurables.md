# Sesion dedicada — Campos y estados configurables

## Como usar este prompt
Copia todo el contenido de la seccion PROMPT
y pegalo al inicio de Claude Code o Claude Chat.

## PROMPT

Lee estos archivos en orden y confirma que entendiste:
1. CLAUDE.md
2. specs/spec_formal.md  
3. specs/campos_configurables.md
4. agents/tdd_agent.md
5. docs/decisions/ADR-010.md
6. docs/decisions/ADR-011.md
7. docs/decisions/ADR-012.md

Luego dime el estado actual del proyecto
y arrancamos con la implementacion.

---

Contexto de la sesion:
Vamos a implementar campos y estados configurables
por proyecto siguiendo el pipeline TDD completo.

Esta funcionalidad permite que cada proyecto
en ReqFlow tenga sus propios campos adicionales
y sus propios estados — sin afectar otros proyectos.

Arquitectura decidida (Camino B):
- Campos base iguales para todos los proyectos
- Campos adicionales definidos por Super-Admin
- Estados configurables por proyecto
- SITESIGO sera el primer proyecto configurado

Orden de implementacion:
FASE 1 — Backend (TDD completo)
  1. Migracion Alembic para 3 tablas nuevas
  2. Modelos SQLAlchemy
  3. Tests unitarios (Red primero)
  4. Repositorios y servicios (Green)
  5. Endpoints FastAPI
  6. Calculo dias habiles Colombia
  7. Tests de integracion
  8. Configurar SITESIGO con sus campos y estados

FASE 2 — Frontend
  1. Vista configuracion proyecto (Super-Admin)
  2. Formulario nuevo requerimiento dinamico
  3. Dashboard con campos del proyecto
  4. Estados del proyecto en el timeline

Reglas que nunca se rompen:
- Tests antes que codigo (TDD)
- Spec antes que implementacion
- Cada decision importante va en un ADR
- CLAUDE.md se actualiza al terminar

Archivos de referencia:
- specs/campos_configurables.md → spec completa
- specs/spec_formal.md → reglas base RN-01 a RN-25
- docs/decisions/ → ADRs existentes
