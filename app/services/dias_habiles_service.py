# -*- coding: utf-8 -*-
from datetime import date, timedelta
import holidays


def calcular_dias_habiles(fecha_inicio: date, fecha_final: date) -> int:
    if fecha_final <= fecha_inicio:
        return 0
    festivos = holidays.Colombia(years=range(fecha_inicio.year, fecha_final.year + 1))
    count = 0
    dia = fecha_inicio
    while dia < fecha_final:
        if dia.weekday() < 5 and dia not in festivos:
            count += 1
        dia += timedelta(days=1)
    return count
