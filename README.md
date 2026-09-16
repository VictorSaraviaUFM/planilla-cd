# Planilla

Cálculo de planilla mensual en Python. Proyecto base de la **Hoja de Trabajo 3** de
Calidad y Automatización en Ingeniería de Software, UFM 2026.

El código funciona y cumple las reglas de abajo. No trae tests ni pipeline: eso es el trabajo.

```bash
uv sync
uv run planilla salario_base=4000 horas_extra=8 dias_trabajados=30 cuota_prestamo=500
```

## Qué hay que hacer

**1. Unit tests.** Una suite con `pytest` sobre las reglas de la planilla, aplicando las
técnicas de la HDT 2: particiones de equivalencia, valores frontera y tabla de decisión.

**2. Pipeline.** Un workflow en `.github/workflows/ci.yml` que:

- dispare en `push` y en `pull request` contra `main`;
- corra `ruff check .` y la suite con coverage;
- cachee las dependencias entre runs;
- fije cada action de terceros por hash de commit, no por tag.

**3. Coverage gate.** `--cov-fail-under` en no menos de 80, justificado en una línea. El gate cuenta todo `src/planilla`, así que la CLI también entra: probando solo las reglas de negocio el umbral no se alcanza.

La cobertura mínima es 95%. Se revisa todo `src/planilla`, incluida la CLI, para asegurar que las reglas y el uso por terminal sigan funcionando. La suite actual llega al 99%, así que el límite es exigente pero realista.

**4. Evidencia.** Dos runs con su SHA: uno **rojo**, rompiendo algo a propósito, y uno
**verde** con el arreglo. Un pipeline que nunca falló no demuestra que la puerta sirva.

El repo llega con findings de `ruff` puestos a propósito. Mientras sigan ahí, el pipeline
no pasa.

## Reglas de la planilla

Son la **base de prueba**, o sea lo que decide si un resultado es correcto. Están
simplificadas para el ejercicio y no sirven como referencia laboral ni fiscal.

Entradas: `salario_base`, `horas_extra`, `dias_trabajados`, `afiliado_igss`,
`cuota_prestamo`.

| Concepto | Regla | Entrada válida |
|---|---|---|
| Valor hora | salario base entre 240 | salario base mayor que cero |
| Horas extra | valor hora por 1.5 | de 0 a 48 al mes |
| Salario ordinario | salario base más horas extra | |
| Bonificación | Q250 con el mes completo, proporcional si no | de 0 a 30 días |
| IGSS | 4.83% del salario ordinario, solo si está afiliado | |
| ISR | doceava parte del ISR anual sobre la renta imponible, que es el salario base por 12 menos Q48,000 de deducción única | |
| Préstamo | se descuenta de último, sin dejar el líquido bajo el 30% del salario ordinario | cuota no negativa |
| Líquido | ordinario más bonificación, menos IGSS, ISR y préstamo | |

La bonificación queda fuera del IGSS y del ISR.

| Renta imponible anual | ISR anual |
|---|---|
| cero o menos | no paga |
| hasta Q300,000 | 5% |
| más de Q300,000 | Q15,000 más 7% del excedente |

## Entrega

Jueves 17 de septiembre de 2026, 23:59, por MiU. Individual. El fork queda público,
porque los runs de Actions se califican desde ahí.

`carne.zip` con: la URL del fork, las dos URLs de run con su SHA, el reporte HTML de
coverage, y la carpeta `.git`.
