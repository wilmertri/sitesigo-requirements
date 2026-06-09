# -*- coding: utf-8 -*-


class ConfigService:
    @staticmethod
    def puede_definir_campos(rol: str) -> bool:
        return rol == "super_admin"

    @staticmethod
    def puede_definir_estados(rol: str) -> bool:
        return rol == "super_admin"
