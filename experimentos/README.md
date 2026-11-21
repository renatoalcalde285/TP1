# Adaptación LoRA de Qwen2.5-VL-3B con texto clínico sintético: evaluación en escritura real (Rodrigo) y control de texto

Código, predicciones y resultados que respaldan las tablas del artículo *Short paper v2.2.5*.
Todo lo que aparece en las Tablas 2 a 5 y en la Figura 1 se puede **verificar sin GPU** con un solo comando:

```bash
pip install pandas rapidfuzz scipy numpy matplotlib
python src/verificar_tablas.py      # recalcula CER/WER desde predictions/ y compara con results/
```

Resultado esperado: 25 líneas `OK` y «Todo coincide» (7 modelos en Rodrigo, 6 en el sintético y 12 en el control de texto).

## De dónde sale cada cifra del artículo

| Artículo | Archivo de resultados | Predicciones | Se produce con |
|---|---|---|---|
| Tabla 2 (Rodrigo, 7 modelos) | `results/rodrigo/tabla_rodrigo.csv` | `predictions/rodrigo/` | `notebooks/evaluacion_completa_v2.ipynb` (partes A, B y C) → `src/analisis_b.py` |
| Tabla 3 (sintético) | `results/synth/tabla_synth.csv` | `predictions/synth/` | ídem (LLaVA-1.6 no se ejecutó en sintético) |
| Tabla 4 (zero-shot frente a LoRA, diferencias pareadas) | `results/*/pares_*.csv` | ídem | `src/analisis_b.py --pairs` |
| Errores en cifras, fechas y unidades | `results/synth/criticos_synth.csv` | `predictions/synth/` | `src/analisis_b.py` |
| Modernización de grafías («vn», «non», «rei») | `results/rodrigo/modernizacion_rodrigo.csv` | `predictions/rodrigo/` | `src/analisis_b.py` |
| Tabla 5 y Figura 1 (control de texto) | `results/control/` | `predictions/control/` | `notebooks/control_texto.ipynb` |
| Adaptador LoRA | `adapter/` (configuración e hiperparámetros) | | `src/train_qwen_lora.py` |

Nombres de modelo en los CSV: `qwen25vl` = Qwen2.5-VL-7B fp16; `qwen25vl7b_4bit` = 7B NF4; `qwen25vl3b` = 3B zero-shot; `qwen25vl3b_lora` = 3B + LoRA; `trocr`, `florence2`, `llava16`.

## Cómo repetir el análisis estadístico

```bash
python src/analisis_b.py --rodrigo predictions/rodrigo --synth predictions/synth --out salida \
  --pairs qwen25vl3b:qwen25vl3b_lora,qwen25vl:qwen25vl7b_4bit
```
Bootstrap con B = 2 000 y semilla 42 que remuestrea **páginas** (Rodrigo) o **historias** (sintético), no líneas sueltas; las diferencias entre modelos son pareadas.

## Cómo repetir las inferencias (requiere GPU, p. ej. 2×T4 en Kaggle)

1. **Rodrigo.** Descargar el corpus del repositorio oficial y usar la partición oficial de prueba (5 010 líneas, 205 páginas). Aquí no se redistribuye.
2. **Corpus sintético.** `src/emnist_to_folders.py` convierte el CSV de EMNIST (*by-class*) y `src/generate_synthetic_hc.py` genera las historias con los textos de SPACCC (Zenodo). Semilla de división por historia: 42 (600/200/200).
3. **Entrenamiento.** El comando exacto está en `adapter/hiperparametros_entrenamiento.json`. El docstring de `src/train_qwen_lora.py` menciona el 7B, pero el adaptador se entrenó con `--model Qwen/Qwen2.5-VL-3B-Instruct`.
4. **Evaluación.** `notebooks/evaluacion_completa_v2.ipynb`: cambiar `PARTE` a `"A"`, `"B"` y `"C"` y ejecutar cada vez. **Esta es la versión que corresponde al artículo** (partición completa, bootstrap por página e historia); versiones anteriores del notebook evaluaban 500 líneas con bootstrap por línea.
5. **Control de texto.** `notebooks/control_texto.ipynb` (misma semilla de generación, 2026; 60 páginas por condición).

## Qué no está en este repositorio

- **Pesos del adaptador** (`adapter_model.safetensors`, ~120 MB): publicados en Zenodo,
  DOI [10.5281/zenodo.24409936](https://doi.org/10.5281/zenodo.24409936).
- **Registros de entrenamiento** (`trainer_state.json`, curva de pérdida): no se conservaron. Se conserva la configuración completa.
- **Imágenes sintéticas, textos de SPACCC y de Rodrigo**: se regeneran o descargan de sus fuentes (licencias propias). En `predictions/control/*/manifest.csv` figuran los textos de referencia de cada condición.
- **Variabilidad entre semillas de entrenamiento**: hay una sola semilla de entrenamiento (42).

## Limitaciones declaradas

Un solo manuscrito del siglo XVI como escritura real; corpus sintético de caracteres aislados de EMNIST sin ligaduras; sin historias clínicas reales; el control de texto no incluye la celda de escritura real con texto clínico; el entrenamiento usó 4 bits y un *prompt* distinto del de evaluación. Detalle en la sección «Amenazas a la validez» del artículo.

## Licencias y datos

- **Código** de este repositorio: MIT (ver `LICENSE`).
- **Adaptador LoRA** (Zenodo): PolyForm Noncommercial 1.0.0, solo para investigación y fines no comerciales.
  Deriva de Qwen2.5-VL-3B-Instruct, que se rige además por su licencia Qwen Research (no comercial).

- **Datos de terceros**, con sus propias licencias: Rodrigo (Serrano et al., 2010; Granell et al., 2018),
  EMNIST (Cohen et al., 2017) y SPACCC (Zenodo). Este repositorio no los redistribuye: solo incluye
  predicciones y manifiestos. SPACCC está bajo CC BY 4.0. Rodrigo y EMNIST no declaran una licencia
  de redistribución explícita; se usan conforme a los términos de sus fuentes.

## Cómo citar

- Repositorio: `https://github.com/renatoalcalde285/TP1`
- Adaptador: Muñico Soto, A. J. (2026). *Adaptador LoRA de Qwen2.5-VL-3B entrenado con historias clínicas
  sintéticas en español* (v2) [Modelo]. Zenodo. https://doi.org/10.5281/zenodo.24409936
