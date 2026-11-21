#!/usr/bin/env python3
"""Análisis del grupo B (sin entrenar) sobre las predicciones por línea.
Uso:
  python analisis_b.py --rodrigo bench_rodrigo --synth bench_synth --out salida \
      --pairs qwen25vl3b:qwen25vl3b_lora
Cada carpeta contiene preds_<modelo>.csv (id, ref, raw, pred, latency_s, error) y meta_<modelo>.json.
"""
import argparse, json, re, unicodedata, itertools
from pathlib import Path
import numpy as np, pandas as pd
from rapidfuzz.distance import Levenshtein
from scipy import stats
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

B, SEED = 2000, 42

# ---------- normalización (idéntica a la del cuaderno de evaluación) ----------
def norm_basic(s):
    s = unicodedata.normalize("NFC", str(s)); return re.sub(r"\s+", " ", s).strip()
def norm_strict(s):
    s = norm_basic(s).lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^\w\s]", "", s); return re.sub(r"\s+", " ", s).strip()

def cluster_of(test, i):
    """historia (sintético) o página (Rodrigo): todo salvo el último sufijo _NN"""
    return i.rsplit("_", 1)[0]

def line_stats(df):
    """errores y tamaños por línea para las 4 métricas"""
    out = {}
    for tag, nf in (("c", norm_basic), ("cn", norm_strict)):
        r = [nf(x) for x in df["ref"].astype(str)]; h = [nf(x) for x in df["pred"].fillna("").astype(str)]
        out[f"e_{tag}"] = np.array([Levenshtein.distance(a, b) for a, b in zip(r, h)])
        out[f"n_{tag}"] = np.array([len(a) for a in r])
        out[f"e_w{tag}"] = np.array([Levenshtein.distance(a.split(), b.split()) for a, b in zip(r, h)])
        out[f"n_w{tag}"] = np.array([len(a.split()) for a in r])
    return pd.DataFrame(out, index=df["id"].values)

METRICS = {"CER": ("e_c", "n_c"), "WER": ("e_wc", "n_wc"), "CER norm": ("e_cn", "n_cn"), "WER norm": ("e_wcn", "n_wcn")}

def load_dir(d):
    d = Path(d); res = {}
    for f in sorted(d.glob("preds_*.csv")):
        key = f.stem[6:]
        p = pd.read_csv(f, keep_default_na=False)
        meta = json.load(open(d / f"meta_{key}.json")) if (d / f"meta_{key}.json").exists() else {}
        res[key] = (p, meta)
    return res

def ci(x): return np.percentile(x, [2.5, 97.5])
def fmt(p, lo, hi, dec=2, sign=False):
    s = "+" if sign else ""
    return f"{p:{s}.{dec}f} [{lo:{s}.{dec}f}, {hi:{s}.{dec}f}]"

def boot_idx(rng, K): return rng.integers(0, K, size=(B, K))

def analyze(test, d, pairs, out, cluster=True):
    data = load_dir(d)
    if not data: print(f"[{test}] sin preds en {d}"); return
    ids_common = None
    for k, (p, _) in data.items():
        s = set(p["id"]); ids_common = s if ids_common is None else ids_common & s
    ids = sorted(ids_common)
    print(f"[{test}] modelos: {list(data)} | líneas comunes: {len(ids)}")
    L = {k: line_stats(p.set_index("id", drop=False).loc[ids].reset_index(drop=True).assign(id=ids)) for k, (p, _) in data.items()}
    cl = np.array([cluster_of(test, i) for i in ids]); uc = np.array(sorted(set(cl))); K = len(uc)
    cidx = np.searchsorted(uc, cl)
    rng = np.random.default_rng(SEED)
    ci_idx = boot_idx(rng, K)             # remuestreo por historia/página (compartido: permite diferencias pareadas)
    li_idx = rng.integers(0, len(ids), size=(B, len(ids)))   # remuestreo por línea (solo para comparar anchos)
    def csum(arr): return np.bincount(cidx, weights=arr, minlength=K)
    rows, boots = [], {}
    for k, st in L.items():
        row = {"modelo": k, "n_líneas": len(ids), "n_clusters": K,
               "caracteres_ref": int(st["n_c"].sum()), "palabras_ref": int(st["n_wc"].sum())}
        for m, (e, n) in METRICS.items():
            ce, cn = csum(st[e].values), csum(st[n].values)
            pt = 100 * ce.sum() / cn.sum()
            bs = 100 * ce[ci_idx].sum(1) / cn[ci_idx].sum(1); boots[(k, m)] = bs
            lo, hi = ci(bs); row[m + " (%)"] = pt; row[m + " IC95 (cluster)"] = fmt(pt, lo, hi)
            if m == "CER":
                bl = 100 * st[e].values[li_idx].sum(1) / st[n].values[li_idx].sum(1)
                llo, lhi = ci(bl); row["CER IC95 (línea)"] = fmt(pt, llo, lhi)
                row["ancho IC cluster / línea"] = round((hi - lo) / (lhi - llo), 2)
        p, meta = data[k]; lat = p["latency_s"].values
        row.update({"lat_media_s": round(lat.mean(), 3), "lat_p95_s": round(np.percentile(lat, 95), 3),
                    "VRAM_pico_GB": meta.get("vram_peak_gb"), "GPU_usadas": meta.get("n_gpus_used"),
                    "% vacías": round(100 * (p["pred"].astype(str).str.strip() == "").mean(), 2),
                    "% alucinación": round(100 * np.mean([len(str(h)) > 2 * len(str(r)) + 10 for r, h in zip(p["ref"], p["pred"])]), 2)})
        rows.append(row)
    tab = pd.DataFrame(rows).sort_values("CER (%)"); tab.to_csv(out / f"tabla_{test}.csv", index=False)
    # ---- pares: diferencia pareada por cluster ----
    prow = []
    for a, b in pairs:
        if a not in L or b not in L: continue
        for m, (e, n) in METRICS.items():
            d_bs = boots[(b, m)] - boots[(a, m)]
            pa = 100 * L[a][e].sum() / L[a][n].sum(); pb = 100 * L[b][e].sum() / L[b][n].sum()
            lo, hi = ci(d_bs)
            row = {"par (a→b)": f"{a}→{b}", "métrica": m, "a": round(pa, 2), "b": round(pb, 2),
                   "Δ=b−a [IC95 cluster]": fmt(pb - pa, lo, hi, sign=True), "p(Δ≥0)": round(float(np.mean(d_bs >= 0)), 4)}
            if m == "CER":
                ca = 100 * csum(L[a][e].values) / csum(L[a][n].values); cb = 100 * csum(L[b][e].values) / csum(L[b][n].values)
                dd = cb - ca
                try: w = stats.wilcoxon(dd, zero_method="wilcox"); pw = w.pvalue
                except ValueError: pw = float("nan")
                ranks = stats.rankdata(np.abs(dd[dd != 0])); sg = np.sign(dd[dd != 0])
                r_rb = (ranks[sg > 0].sum() - ranks[sg < 0].sum()) / max(ranks.sum(), 1e-9)
                row.update({"Wilcoxon p (por cluster)": pw, "r rango-biserial": round(float(r_rb), 3),
                            "dz de Cohen": round(float(dd.mean() / dd.std(ddof=1)), 3) if dd.std(ddof=1) > 0 else float("nan"),
                            "% clusters peores": round(100 * float(np.mean(dd > 0)), 1)})
            prow.append(row)
        # histograma / dispersión por línea (CER por línea, no por corpus)
        ea = L[a]["e_c"] / np.maximum(L[a]["n_c"], 1); eb = L[b]["e_c"] / np.maximum(L[b]["n_c"], 1)
        dl = 100 * (eb - ea).values
        fig, ax = plt.subplots(1, 2, figsize=(9, 3.4), dpi=300)
        ax[0].hist(dl, bins=np.arange(-50, 51, 2.5), color="#6b7a8f", edgecolor="white", linewidth=.5)
        ax[0].axvline(0, color="black", lw=1)
        ax[0].set_xlabel(f"Δ CER por línea (puntos): {b} − {a}"); ax[0].set_ylabel("líneas")
        txt = f"mejor: {(dl<0).sum()}  igual: {(dl==0).sum()}  peor: {(dl>0).sum()}"
        ax[0].set_title(txt, fontsize=9)
        ax[1].scatter(100 * ea, 100 * eb, s=4, alpha=.35, color="#6b7a8f", linewidths=0)
        mx = float(max(100 * ea.max(), 100 * eb.max())); ax[1].plot([0, mx], [0, mx], color="black", lw=1)
        ax[1].set_xlabel(f"CER por línea (%) {a}"); ax[1].set_ylabel(f"CER por línea (%) {b}")
        for s in ("top", "right"): ax[0].spines[s].set_visible(False); ax[1].spines[s].set_visible(False)
        fig.tight_layout(); fig.savefig(out / f"fig_delta_cer_{test}_{a}_vs_{b}.png"); plt.close(fig)
    if prow: pd.DataFrame(prow).to_csv(out / f"pares_{test}.csv", index=False)
    # ---- figura: CER con IC por modelo ----
    t = tab.sort_values("CER (%)"); fig, ax = plt.subplots(figsize=(6.2, 0.45 * len(t) + 1), dpi=300)
    err = []
    for k in t["modelo"]:
        lo, hi = ci(boots[(k, "CER")]); pt = float(t.loc[t.modelo == k, "CER (%)"].iloc[0]); err.append((pt - lo, hi - pt))
    ax.barh(t["modelo"], t["CER (%)"], xerr=np.array(err).T, color="#6b7a8f", edgecolor="black", linewidth=.6, capsize=3, height=.55)
    ax.invert_yaxis(); ax.set_xlabel("CER (%), IC 95 % por " + ("historia/página")); ax.set_title(f"Conjunto: {test}", fontsize=10)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(out / f"fig_cer_ic_{test}.png"); plt.close(fig)
    return L, ids, data

# ---------- error en datos críticos (solo con texto de referencia conocido: sintético) ----------
UNITS = r"(?:mg|mcg|µg|g|kg|ml|dl|mmol|mmhg|ui|cm|mm|%|gy|cgy|mci|bpm|rpm|mg/dl|mg/kg|ml/h)"
CRIT = re.compile(rf"^(?:.*\d.*|{UNITS}\.?)$", re.I)   # contiene cifra (cifras, fechas, dosis) o es una unidad
def critical_errors(df):
    tot = err = lines_err = lines_with = 0; per = {"cifras/fechas": [0, 0], "unidades": [0, 0]}
    for r, h in zip(df["ref"].astype(str), df["pred"].fillna("").astype(str)):
        rw, hw = norm_basic(r).split(), norm_basic(h).split()
        bad = set()
        for tag, i1, i2, j1, j2 in Levenshtein.opcodes(rw, hw):
            if tag in ("replace", "delete"): bad.update(range(i1, i2))
        crit = [i for i, w in enumerate(rw) if CRIT.match(w)]
        if not crit: continue
        lines_with += 1; e = [i for i in crit if i in bad]
        tot += len(crit); err += len(e); lines_err += bool(e)
        for i in crit:
            k = "cifras/fechas" if re.search(r"\d", rw[i]) else "unidades"
            per[k][0] += 1; per[k][1] += i in bad
    return {"tokens_críticos": tot, "tasa_error_tokens_críticos (%)": round(100 * err / max(tot, 1), 2),
            "líneas_con_dato_crítico": lines_with, "% líneas con ≥1 error crítico": round(100 * lines_err / max(lines_with, 1), 2),
            "tasa_error_cifras/fechas (%)": round(100 * per["cifras/fechas"][1] / max(per["cifras/fechas"][0], 1), 2),
            "tasa_error_unidades (%)": round(100 * per["unidades"][1] / max(per["unidades"][0], 1), 2)}

# ---------- análisis de errores cuantitativo (Rodrigo) ----------
def word_errors(df, modern=("non", "rei", "vn")):
    sub = dele = ins = 0; types = {"visual (dist≤2 sin tildes/mayús.)": 0, "léxica (dist>2)": 0, "grafía/mayúscula/tilde": 0}
    ex = []
    for i, r, h in zip(df["id"], df["ref"].astype(str), df["pred"].fillna("").astype(str)):
        rw, hw = norm_basic(r).split(), norm_basic(h).split()
        for tag, i1, i2, j1, j2 in Levenshtein.opcodes(rw, hw):
            if tag == "delete": dele += i2 - i1
            elif tag == "insert": ins += j2 - j1
            elif tag == "replace":
                for a, b in zip(rw[i1:i2], hw[j1:j2]):
                    sub += 1
                    if norm_strict(a) == norm_strict(b): t = "grafía/mayúscula/tilde"
                    elif Levenshtein.distance(norm_strict(a), norm_strict(b)) <= 2: t = "visual (dist≤2 sin tildes/mayús.)"
                    else: t = "léxica (dist>2)"
                    types[t] += 1; ex.append((i, a, b, t))
                extra = abs((i2 - i1) - (j2 - j1)); dele += max((i2 - i1) - (j2 - j1), 0); ins += max((j2 - j1) - (i2 - i1), 0)
    # modernización: líneas cuya referencia contiene la grafía antigua y la predicción no
    mod = {}
    for w in modern:
        n_ref = sum(w in norm_basic(r).split() for r in df["ref"].astype(str)); n_pred = sum(w in norm_basic(h).split() for h in df["pred"].fillna("").astype(str))
        mod[w] = (n_ref, n_pred)
    return {"sustituciones": sub, "eliminaciones": dele, "inserciones": ins, **types}, mod, pd.DataFrame(ex, columns=["id", "ref", "pred", "tipo_auto"])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rodrigo"); ap.add_argument("--synth"); ap.add_argument("--out", default="salida_b")
    ap.add_argument("--pairs", default="qwen25vl3b:qwen25vl3b_lora")
    ap.add_argument("--muestra-errores", type=int, default=200)
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    pairs = [tuple(p.split(":")) for p in a.pairs.split(",") if p]
    for test, d in (("rodrigo", a.rodrigo), ("synth", a.synth)):
        if not d: continue
        r = analyze(test, d, pairs, out)
        if not r: continue
        L, ids, data = r
        if test == "synth":
            rows = [{"modelo": k, **critical_errors(p)} for k, (p, _) in data.items()]
            pd.DataFrame(rows).to_csv(out / "criticos_synth.csv", index=False); print(pd.DataFrame(rows).to_string())
        else:
            rows, mods, samples = [], [], []
            for k, (p, _) in data.items():
                we, mod, ex = word_errors(p); rows.append({"modelo": k, **we})
                for w, (nr, np_) in mod.items(): mods.append({"modelo": k, "grafía": w, "líneas_ref": nr, "líneas_pred": np_})
                if len(ex): samples.append(ex.assign(modelo=k).sample(min(a.muestra_errores, len(ex)), random_state=SEED))
            pd.DataFrame(rows).to_csv(out / "errores_palabra_rodrigo.csv", index=False)
            pd.DataFrame(mods).to_csv(out / "modernizacion_rodrigo.csv", index=False)
            if samples:
                s = pd.concat(samples); s["anotador1"] = ""; s["anotador2"] = ""
                s.to_csv(out / "muestra_errores_para_anotar.csv", index=False)
    print("listo →", out)
if __name__ == "__main__": main()
