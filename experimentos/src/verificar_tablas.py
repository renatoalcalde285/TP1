"""Recalcula el CER/WER globales a partir de las predicciones y los compara con las tablas publicadas.
Uso: python src/verificar_tablas.py   (desde la raíz del repositorio)
Requiere: pandas, rapidfuzz. No necesita GPU ni modelos."""
import sys, re, unicodedata, json
from pathlib import Path
import pandas as pd
from rapidfuzz.distance import Levenshtein
ROOT = Path(__file__).resolve().parents[1]
def nb(s): return re.sub(r"\s+", " ", unicodedata.normalize("NFC", str(s))).strip()
def cer_wer(df):
    r = [nb(x) for x in df["ref"]]; h = [nb(x) for x in df["pred"].fillna("")]
    ec = sum(Levenshtein.distance(a, b) for a, b in zip(r, h)); nc = sum(len(a) for a in r)
    ew = sum(Levenshtein.distance(a.split(), b.split()) for a, b in zip(r, h)); nw = sum(len(a.split()) for a in r)
    return 100 * ec / nc, 100 * ew / nw, len(r)
bad = 0
for ds in ("rodrigo", "synth"):
    tab = pd.read_csv(ROOT / f"results/{ds}/tabla_{ds}.csv").set_index("modelo")
    for f in sorted((ROOT / f"predictions/{ds}").glob("preds_*.csv")):
        k = f.stem[6:]; c, w, n = cer_wer(pd.read_csv(f, keep_default_na=False))
        ok = abs(c - tab.loc[k, "CER (%)"]) < 0.01 and abs(w - tab.loc[k, "WER (%)"]) < 0.01 and n == tab.loc[k, "n_líneas"]
        bad += not ok; print(f"{'OK ' if ok else 'ERR'} {ds:8s} {k:20s} n={n:5d} CER={c:7.2f} WER={w:7.2f}")
ctl = pd.read_csv(ROOT / "results/control/control_2x2_cer.csv"); ctl = ctl[ctl["líneas"] == "todas"].set_index("condición")
for d in sorted((ROOT / "predictions/control").iterdir()):
    cond = d.name[5:]
    for k, col in (("qwen25vl3b", "CER zero-shot"), ("qwen25vl3b_lora", "CER LoRA")):
        c, _, n = cer_wer(pd.read_csv(d / f"preds_{k}.csv", keep_default_na=False))
        pub = float(ctl.loc[cond, col].split()[0]); ok = abs(c - pub) < 0.01 and n == ctl.loc[cond, "n líneas"]
        bad += not ok; print(f"{'OK ' if ok else 'ERR'} control  {cond:18s} {k:16s} n={n:4d} CER={c:6.2f} (publicado {pub:.2f})")
print("\nTodo coincide." if not bad else f"\n{bad} diferencias."); sys.exit(1 if bad else 0)
