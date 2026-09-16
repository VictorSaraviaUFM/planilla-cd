import pytest

from planilla.calculo import (
    Planilla,
    bonificacion_incentivo,
    descuento_igss,
    descuento_isr,
    descuento_prestamo,
    isr_anual,
    liquidar,
    pago_horas_extra,
    resumen,
    salario_ordinario,
    valor_hora,
)


# Particiones de equivalencia: salario base válido e inválido.
@pytest.mark.parametrize("salario", [0, -1])
def test_valor_hora_rechaza_salario_no_positivo(salario):
    with pytest.raises(ValueError, match="salario base"):
        valor_hora(salario)


def test_valor_hora_para_salario_valido():
    assert valor_hora(2400) == pytest.approx(10.0)


# Valores frontera: horas extra entre 0 y 48, inclusivo.
@pytest.mark.parametrize(
    ("horas_extra", "esperado"),
    [
        (0, 0.0),
        (48, 720.0),
    ],
)
def test_pago_horas_extra_en_fronteras_validas(horas_extra, esperado):
    assert pago_horas_extra(2400, horas_extra) == pytest.approx(esperado)


@pytest.mark.parametrize("horas_extra", [-1, 49])
def test_pago_horas_extra_rechaza_valores_fuera_de_rango(horas_extra):
    with pytest.raises(ValueError, match="horas extra"):
        pago_horas_extra(2400, horas_extra)


def test_salario_ordinario_suma_salario_y_horas_extra():
    assert salario_ordinario(2400, 8) == pytest.approx(2520.0)


# Valores frontera: días trabajados de 0 a 30, inclusivo.
@pytest.mark.parametrize(
    ("dias_trabajados", "esperado"),
    [
        (0, 0.0),
        (29, 250 * 29 / 30),
        (30, 250.0),
    ],
)
def test_bonificacion_proporcional_y_mes_completo(dias_trabajados, esperado):
    assert bonificacion_incentivo(dias_trabajados) == pytest.approx(esperado)


@pytest.mark.parametrize("dias_trabajados", [-1, 31])
def test_bonificacion_rechaza_dias_fuera_de_rango(dias_trabajados):
    with pytest.raises(ValueError, match="dias trabajados"):
        bonificacion_incentivo(dias_trabajados)


@pytest.mark.parametrize(
    ("afiliado", "esperado"),
    [
        (True, 48.3),
        (False, 0.0),
        (None, 0.0),
    ],
)
def test_igss_depende_de_afiliacion(afiliado, esperado):
    assert descuento_igss(1000, afiliado) == pytest.approx(esperado)


# Fronteras de los tres tramos del ISR.
@pytest.mark.parametrize(
    ("renta_bruta_anual", "esperado"),
    [
        (48000, 0.0),
        (48001, 0.05),
        (348000, 15000.0),
        (348001, 15000.07),
    ],
)
def test_isr_anual_en_fronteras_de_tramos(renta_bruta_anual, esperado):
    assert isr_anual(renta_bruta_anual) == pytest.approx(esperado)


def test_descuento_isr_es_doceava_parte_del_anual():
    assert descuento_isr(4001) == pytest.approx(0.05)


# Tabla de decisión para el préstamo.
@pytest.mark.parametrize(
    ("liquido_antes", "salario_ordinario_mes", "cuota", "esperado"),
    [
        (1000, 4000, 500, 0.0),  # Ya está por debajo del piso del 30%.
        (1500, 4000, 500, 300.0),  # Se limita al margen disponible.
        (2000, 4000, 500, 500.0),  # Se descuenta la cuota completa.
        (2000, 4000, 0, 0.0),  # No hay cuota.
    ],
)
def test_tabla_decision_descuento_prestamo(
    liquido_antes,
    salario_ordinario_mes,
    cuota,
    esperado,
):
    assert descuento_prestamo(
        liquido_antes,
        salario_ordinario_mes,
        cuota,
    ) == pytest.approx(esperado)


def test_prestamo_rechaza_cuota_negativa():
    with pytest.raises(ValueError, match="prestamo"):
        descuento_prestamo(2000, 4000, -1)


def test_liquidar_calcula_el_desglose_completo():
    resultado = liquidar(
        salario_base=4000,
        horas_extra=8,
        dias_trabajados=30,
        afiliado_igss=True,
        cuota_prestamo=500,
    )

    assert resultado.salario_ordinario == pytest.approx(4200.0)
    assert resultado.bonificacion == pytest.approx(250.0)
    assert resultado.igss == pytest.approx(202.86)
    assert resultado.isr == pytest.approx(0.0)
    assert resultado.prestamo == pytest.approx(500.0)
    assert resultado.liquido == pytest.approx(3747.14)


def test_resumen_muestra_liquido_y_descuentos():
    planilla = Planilla(4200, 250, 202.86, 0, 500, 3747.14)

    assert resumen(planilla) == "Liquido: Q3747.14 | Descuentos: Q702.86"
