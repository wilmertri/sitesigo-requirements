# Especificacion Formal - Gestor de Requerimientos SITESIGO

## Problema
Centralizar la gestion de requerimientos de SITESIGO
que hoy viven dispersos en hojas de calculo,
sin trazabilidad ni ciclo de vida definido.

## Actores
| Actor | Rol |
|---|---|
| Administrador (Fabian) | Gestion completa |
| Funcionario (Alcaldia) | Reporta y consulta |
| Equipo tecnico | Ejecuta y comenta |

## Flujos principales
- F-01: Registrar requerimiento (Admin, Funcionario)
- F-02: Cambiar estado (Admin)
- F-03: Consultar y filtrar lista (Todos)
- F-04: Ver historial de cambios (Todos)
- F-05: Agregar comentarios (Todos)
- F-06: Notificacion email al cambiar estado (Sistema)

## Tipos de requerimiento
- Bug
- Nueva funcionalidad
- Cambio en modulo
- Mejora UX/rendimiento

## Estados
Nuevo | En analisis | En desarrollo | Resuelto | Cerrado | Rechazado

## Reglas de negocio
| ID | Regla |
|---|---|
| RN-01 | titulo, descripcion, tipo y prioridad son obligatorios |
| RN-02 | Solo Admin cambia el estado |
| RN-03 | Funcionario edita solo sus requerimientos en estado Nuevo |
| RN-04 | Cada cambio de estado queda en historial con actor y fecha |
| RN-05 | Email al creador Funcionario al cambiar estado |
| RN-06 | Prioridad solo puede ser Alta, Media o Baja |
| RN-07 | Cerrado y Rechazado son estados terminales |

## Decisiones tomadas
- Ambos Admin y Funcionario pueden crear requerimientos
- Funcionarios ven todos pero editan solo los suyos
- Historial completo de cambios (quien, cuando, de que a que)
- Notificaciones por email (no dentro de la app)