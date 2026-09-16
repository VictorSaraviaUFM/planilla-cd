import sys

from planilla.cli import USO, main, parse_args


def test_parse_args_convierte_numeros_y_conserva_texto():
    assert parse_args(
        ["salario_base=4000", "afiliado_igss=no", "sin_formato"]
    ) == {
        "salario_base": 4000.0,
        "afiliado_igss": "no",
    }


def test_main_muestra_uso_si_no_hay_salario_base(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["planilla"])

    assert main() == 1
    assert capsys.readouterr().out.strip() == USO


def test_main_calcula_planilla_desde_argumentos(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "planilla",
            "salario_base=4000",
            "horas_extra=8",
            "dias_trabajados=30",
            "cuota_prestamo=500",
            "afiliado_igss=si",
        ],
    )

    assert main() == 0
    assert (
        capsys.readouterr().out.strip()
        == "Liquido: Q3747.14 | Descuentos: Q702.86"
    )
