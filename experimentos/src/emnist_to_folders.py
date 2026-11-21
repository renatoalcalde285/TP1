"""
Convierte EMNIST (CSV de Kaggle) en un banco de letras por carpetas para generate_synthetic_hc.py.

Salida:  <out>/<código ASCII en hexadecimal>/<n>.png      (p. ej. 61/000.png es una "a", 41/000.png es una "A")
Cada PNG es de 28x28, tinta negra sobre fondo blanco (como SD19 by_class).

El CSV de EMNIST guarda cada imagen traspuesta (columnas y filas intercambiadas), por eso se corrige con .T.

Uso:
  python emnist_to_folders.py \
     --csv /kaggle/input/emnist/emnist-byclass-train.csv \
     --mapping /kaggle/input/emnist/emnist-byclass-mapping.txt \
     --out /kaggle/working/emnist_byclass --per_class 500
"""
import argparse, random
from pathlib import Path
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("--csv", required=True, type=Path)
ap.add_argument("--mapping", required=True, type=Path)
ap.add_argument("--out", required=True, type=Path)
ap.add_argument("--per_class", type=int, default=500)
ap.add_argument("--seed", type=int, default=0)
a = ap.parse_args()

# mapping: "<etiqueta> <código ASCII>" por línea
asc = {}
for line in a.mapping.read_text().split("\n"):
    p = line.split()
    if len(p) == 2: asc[int(p[0])] = int(p[1])

rng = random.Random(a.seed)
rows = {}                      # etiqueta -> lista de filas (índices en el archivo)
with open(a.csv) as f:
    for i, line in enumerate(f):
        lab = int(line.split(",", 1)[0]); rows.setdefault(lab, []).append(i)
keep = {lab: set(rng.sample(ix, min(a.per_class, len(ix)))) for lab, ix in rows.items()}

count = {}
with open(a.csv) as f:
    for i, line in enumerate(f):
        lab_s, rest = line.split(",", 1); lab = int(lab_s)
        if i not in keep.get(lab, ()): continue
        px = np.array(rest.split(","), dtype=np.uint8).reshape(28, 28).T   # corrige la trasposición
        d = a.out / f"{asc[lab]:02x}"; d.mkdir(parents=True, exist_ok=True)
        n = count.get(lab, 0); count[lab] = n + 1
        Image.fromarray(255 - px).save(d / f"{n:03d}.png")                  # tinta negra sobre blanco
print(f"Clases: {len(count)} | imágenes: {sum(count.values())} → {a.out}")
