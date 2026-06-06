# -*- coding: utf-8 -*-
from app.models.history import CambioEstado
from app.models.requirement import EstadoRequerimiento, Requerimiento, RolUsuario
from app.services.notification_service import NotificationService

_ESTADOS_TERMINALES = {EstadoRequerimiento.cerrado, EstadoRequerimiento.rechazado}


class RequirementService:

    @staticmethod
    def _verificar_no_terminal(requerimiento: Requerimiento, accion: str) -> None:
        if requerimiento.estado in _ESTADOS_TERMINALES:
            nombre = requerimiento.estado.value.capitalize()
            raise ValueError(f"Un requerimiento {nombre} no puede {accion}")

    @staticmethod
    def cambiar_estado(
        requerimiento: Requerimiento,
        nuevo_estado: EstadoRequerimiento,
        rol_usuario: RolUsuario,
        usuario_id: int,
    ) -> Requerimiento:
        RequirementService._verificar_no_terminal(requerimiento, "cambiar de estado")

        if rol_usuario != RolUsuario.administrador:
            raise PermissionError("Solo el Administrador puede cambiar el estado")

        if not isinstance(nuevo_estado, EstadoRequerimiento):
            raise ValueError(f"Estado invalido: {nuevo_estado!r}")

        estado_anterior = requerimiento.estado
        requerimiento.estado = nuevo_estado
        requerimiento.historial.append(
            CambioEstado(
                requerimiento_id=requerimiento.id,
                usuario_id=usuario_id,
                rol_usuario=rol_usuario,
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado,
            )
        )
        if requerimiento.autor_rol == RolUsuario.funcionario:
            try:
                NotificationService.enviar_cambio_estado(
                    email_destinatario=requerimiento.autor_email,
                    titulo_requerimiento=requerimiento.titulo,
                    estado_nuevo=nuevo_estado.value.capitalize(),
                )
            except Exception:
                pass
        return requerimiento

    @staticmethod
    def editar(
        requerimiento: Requerimiento,
        nueva_descripcion: str,
        usuario_id: int,
        rol_usuario: RolUsuario,
    ) -> Requerimiento:
        RequirementService._verificar_no_terminal(requerimiento, "ser editado")

        if rol_usuario == RolUsuario.funcionario:
            if requerimiento.autor_id != usuario_id:
                raise PermissionError("Solo puedes editar tus propios requerimientos")
            if requerimiento.estado != EstadoRequerimiento.nuevo:
                raise PermissionError("Solo puedes editar requerimientos en estado Nuevo")

        requerimiento.descripcion = nueva_descripcion
        return requerimiento
