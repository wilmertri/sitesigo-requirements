# -*- coding: utf-8 -*-


class ProjectService:
    @staticmethod
    def puede_crear_proyecto(rol: str) -> bool:
        return rol == "super_admin"

    @staticmethod
    def puede_gestionar_usuarios(rol_en_proyecto: str) -> bool:
        return rol_en_proyecto in ("super_admin", "administrador")
