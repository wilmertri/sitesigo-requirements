# Spec — Campos y estados configurables por proyecto

## Problema
Cada proyecto tiene necesidades diferentes.
SITESIGO necesita campos que no existen en
el modelo generico de ReqFlow.

## Decision de arquitectura
Camino B: ReqFlow generico + campos opcionales
por proyecto. Los campos base son iguales para
todos. Los campos adicionales los define el
Super-Admin por proyecto.

## Reglas de negocio
RN-20: Solo Super-Admin define campos personalizados
RN-21: Tipos soportados: texto, fecha, numero, lista
RN-22: dias_habiles es calculado automaticamente
       entre fecha_inicio y fecha_final
       sin domingos ni festivos colombianos
RN-23: Solo Super-Admin define estados por proyecto
RN-24: Cada proyecto tiene su lista de estados
RN-25: Al crear requerimiento aparecen campos
       y estados del proyecto

## Modelo de datos nuevo
ProyectoConfigCampo:
  id, proyecto_id, nombre, clave, tipo,
  opciones (JSON), obligatorio, orden

ProyectoConfigEstado:
  id, proyecto_id, nombre, color,
  orden, es_terminal

RequerimientoValorCampo:
  id, requerimiento_id, campo_id, valor

## Configuracion SITESIGO

### Campos adicionales:
1. Observaciones - texto - no obligatorio
2. Proceso - lista - opciones:
   Seguimiento Fisico, Seguimiento Financiero,
   Banco de Proyectos, Politica Publica,
   Informes, Todos
3. Fecha Inicio - fecha - no obligatorio
4. Fecha Final - fecha - no obligatorio
5. Dias habiles - calculado (Fecha Final - Fecha Inicio
   sin domingos ni festivos Colombia)
6. Obligacion contractual - numero - no obligatorio

### Estados del proyecto:
1. En Espera - #94a3b8 - no terminal
2. En Desarrollo - #3b82f6 - no terminal
3. En Revision - #f59e0b - no terminal
4. Entregado - #10b981 - terminal
5. Cancelado - #ef4444 - terminal

## Impacto en el sistema
Backend:
- 3 tablas nuevas (migracion Alembic)
- Endpoints CRUD para campos y estados
- Endpoint para calcular dias habiles
- Requerimientos guardan valores de campos

Frontend:
- Vista configuracion del proyecto (Super-Admin)
- Formulario nuevo requerimiento dinamico
- Dashboard muestra campos del proyecto
