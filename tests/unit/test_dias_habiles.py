# -*- coding: utf-8 -*-
from datetime import date
from app.services.dias_habiles_service import calcular_dias_habiles


def test_semana_laboral_completa():
    # lunes 5 a lunes 12 enero 2026: 5 dias habiles (rango exclusivo en fin)
    assert calcular_dias_habiles(date(2026, 1, 5), date(2026, 1, 12)) == 5


def test_excluye_festivo_colombiano():
    # 1 ene (Año Nuevo) a 5 ene: solo el 2 es habil (3 y 4 son fin de semana)
    assert calcular_dias_habiles(date(2026, 1, 1), date(2026, 1, 5)) == 1


def test_excluye_semana_santa():
    # 30 mar a 6 abr 2026: Jueves Santo (2 abr) y Viernes Santo (3 abr) excluidos
    # dias habiles: lun 30, mar 31, mie 1 = 3
    assert calcular_dias_habiles(date(2026, 3, 30), date(2026, 4, 6)) == 3


def test_misma_fecha_devuelve_cero():
    assert calcular_dias_habiles(date(2026, 1, 5), date(2026, 1, 5)) == 0


def test_fin_antes_de_inicio_devuelve_cero():
    assert calcular_dias_habiles(date(2026, 1, 12), date(2026, 1, 5)) == 0
