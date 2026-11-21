"""
Genera historias clínicas SINTÉTICAS manuscritas sobre hoja en blanco, usando:
  - letras manuscritas de NIST SD19 (o cualquier banco de letras con una carpeta por carácter)
  - texto clínico en español de SPACCC (opcional; si no se da, usa frases internas)
  - listas internas de diagnósticos oncológicos, fármacos y abreviaturas médicas
  - datos de paciente 100% inventados

Salida (en --out_dir):
  pages/hc_00000.jpg            imagen de la página completa
  pages.jsonl                   {"id","image","text" (transcripción con \\n), "fields": {...}}
  lines/hc_00000_03.png         recorte de cada línea
  lines.jsonl                   {"id","image","text"}  -> sirve directo para train_qwen_lora.py
  preview_lines.png             (con --preview) mosaico de las primeras líneas para revisar a ojo

Banco de letras soportado (--char_root):
  A) SD19 "by_class": carpetas con el código ASCII en hexadecimal
       by_class/61/... -> 'a'   by_class/41/... -> 'A'   by_class/30/... -> '0'
  B) Genérico: una carpeta por carácter  ->  letras/a/*.png, letras/A/*.png
  (Busca las imágenes recursivamente dentro de cada carpeta.)

Limitaciones conocidas (dilo en la tesis):
  - SD19 es letra de imprenta SEPARADA, no cursiva ligada.
  - ñ, tildes y signos (. , : / ( ) ° - +) se DIBUJAN por código.
  - Letras de distintos escritores: se unifica el estilo por documento (inclinación, grosor, tamaño, tinta).

Uso:
  python generate_synthetic_hc.py --char_root SD19/by_class --text_dir SPACCC --out_dir synth --n 1000 --preview
"""
import argparse
import json
import random
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

IMG_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}

# ----------------------------------------------------------------------------- caracteres
# Posición vertical de cada carácter en unidades de x-height (y hacia abajo, línea base = 0)
X_LOWER = set("acemnorsuvwxz")
ASCEND = set("bdhkl")
DESCEND = set("gpqy")
ACCENTS = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U"}
TILDE = {"ñ": "n", "Ñ": "N"}
DIAER = {"ü": "u", "Ü": "U"}
DRAWN_PUNCT = set(".,:;-/()°+")


def vbox(ch):
    """(top, bottom) en unidades de x-height relativas a la línea base."""
    if ch in X_LOWER:
        return -1.0, 0.0
    if ch in ASCEND or ch == "f":
        return -1.6, 0.0
    if ch == "t":
        return -1.35, 0.0
    if ch == "i":
        return -1.45, 0.0
    if ch == "j":
        return -1.45, 0.6
    if ch in DESCEND:
        return -1.0, 0.6
    return -1.5, 0.0  # mayúsculas y dígitos


# ----------------------------------------------------------------------------- contenido clínico
DIAGNOSTICOS = [
    # (diagnóstico, sexo permitido: "M", "F" o None = ambos, ¿admite lateralidad?)
    ("Ca de mama", "F", True), ("Ca gástrico", None, False), ("Ca de cérvix", "F", False),
    ("Ca de próstata", "M", False), ("Ca pulmonar", None, True), ("Ca colorrectal", None, False),
    ("Ca de tiroides", None, False), ("Ca de ovario", "F", True), ("Ca hepatocelular", None, False),
    ("Ca de páncreas", None, False), ("Ca de vejiga", None, False), ("Ca renal", None, True),
    ("Linfoma no Hodgkin", None, False), ("Linfoma de Hodgkin", None, False),
    ("Leucemia linfoblástica aguda", None, False), ("Leucemia mieloide aguda", None, False),
    ("Mieloma múltiple", None, False), ("Melanoma", None, False), ("Sarcoma de partes blandas", None, False),
    ("Osteosarcoma", None, True), ("Ca de esófago", None, False), ("Ca de endometrio", "F", False),
    ("Ca de laringe", None, False), ("Tumor cerebral", None, False), ("Ca de testículo", "M", True),
]
LATERALIDAD = ["", "", " izq.", " der."]
ESTADIOS = ["", "", " EC I", " EC IIA", " EC IIB", " EC IIIA", " EC IIIB", " EC IV", " T2N1M0", " T3N0M0"]
COMORB = ["HTA", "DM2", "anemia", "ERC", "hipotiroidismo", "EPOC", "obesidad", "desnutrición"]
FARMACOS = [
    "paclitaxel", "cisplatino", "carboplatino", "doxorrubicina", "ciclofosfamida", "capecitabina",
    "5-fluorouracilo", "oxaliplatino", "docetaxel", "gemcitabina", "vincristina", "metotrexato",
    "tamoxifeno 20 mg VO c/24h", "anastrozol 1 mg VO c/24h", "tramadol 50 mg EV c/8h",
    "metamizol 1 g EV c/8h", "paracetamol 1 g VO c/8h", "ondansetrón 8 mg EV c/8h",
    "omeprazol 20 mg VO c/24h", "dexametasona 4 mg EV c/12h", "morfina 5 mg SC c/4h",
    "ceftriaxona 2 g EV c/24h", "enoxaparina 40 mg SC c/24h", "metoclopramida 10 mg EV c/8h",
    "filgrastim 300 mcg SC", "ácido fólico 1 tab VO c/24h", "sulfato ferroso 1 tab VO c/24h",
]
CICLOS = ["", "", " ciclo 1", " ciclo 2", " ciclo 3", " C4", " C6"]
EVOL_INTERNAS = [
    "Paciente refiere dolor abdominal leve, tolera vía oral",
    "Paciente en regular estado general, afebril, hemodinámicamente estable",
    "Se indica control con hemograma y perfil hepático en 7 días",
    "Refiere náuseas post quimioterapia, sin vómitos",
    "Presión arterial 120/80, frecuencia cardiaca 78, saturación 96%",
    "Paciente con buena tolerancia al tratamiento, se continúa esquema",
    "Se solicita tomografía computarizada de tórax y abdomen",
    "Herida operatoria limpia, sin signos de infección",
    "Paciente con dolor controlado, deambula sin ayuda",
    "Se programa radioterapia según evaluación",
]
NOMBRES_M = ["Juan", "José", "Luis", "Carlos", "Jorge", "Pedro", "Miguel", "Víctor", "Raúl", "Óscar",
             "César", "Félix", "Ángel", "Hugo", "Mario", "Andrés", "Julio", "Ramón", "Tomás", "Rubén"]
NOMBRES_F = ["María", "Rosa", "Carmen", "Ana", "Elena", "Lucía", "Julia", "Teresa", "Gloria", "Patricia",
             "Silvia", "Norma", "Isabel", "Martha", "Sonia", "Inés", "Beatriz", "Mónica", "Raquel", "Nelly"]
APELLIDOS = ["Quispe", "Flores", "Sánchez", "Rodríguez", "García", "Rojas", "Mamani", "Huamán", "Torres",
             "Vargas", "Chávez", "Ramírez", "Castillo", "Mendoza", "Díaz", "Gutiérrez", "Ramos", "Espinoza",
             "Vásquez", "Cruz", "Paredes", "Cárdenas", "Salazar", "Núñez", "Córdova", "Aguilar", "Ríos"]

# Reemplazos típicos de notas médicas (se aplica cada uno con probabilidad p)
ABREVIATURAS = [
    (r"\bhipertensión arterial\b", "HTA"), (r"\bdiabetes mellitus tipo 2\b", "DM2"),
    (r"\bdiabetes mellitus\b", "DM"), (r"\bpaciente\b", "pcte"), (r"\bPaciente\b", "Pcte"),
    (r"\btratamiento\b", "tto"), (r"\bdiagnóstico\b", "dx"), (r"\bantecedentes\b", "antec."),
    (r"\bcada (\d+) horas\b", r"c/\1h"), (r"\bvía oral\b", "VO"), (r"\b(endovenos[oa]|intravenos[oa])\b", "EV"),
    (r"\babdominal\b", "abd."), (r"\bradiografía\b", "Rx"), (r"\btomografía computarizada\b", "TC"),
    (r"\bquimioterapia\b", "QT"), (r"\bradioterapia\b", "RT"), (r"\bpresión arterial\b", "PA"),
    (r"\bfrecuencia cardiaca\b", "FC"), (r"\bfrecuencia respiratoria\b", "FR"), (r"\bcon\b", "c/"),
    (r"\bsin\b", "s/"), (r"\baños\b", "a"), (r"\bcontrol\b", "ctrl"), (r"\bhemograma\b", "Hgma"),
    (r"\bsaturación\b", "Sat"), (r"\btemperatura\b", "T°"),
]


def abreviar(text, rng, p=0.6):
    for pat, rep in ABREVIATURAS:
        if rng.random() < p:
            text = re.sub(pat, rep, text)
    return text


def cargar_frases(text_dir, rng, max_frases=50000):
    """Frases de SPACCC (o cualquier carpeta de .txt), agrupadas por caso clínico.
    Devuelve una lista de casos; cada caso es una lista de frases en orden."""
    casos, total = [], 0
    if text_dir:
        files = sorted(Path(text_dir).rglob("*.txt"))
        rng.shuffle(files)
        for f in files:
            raw = f.read_text(encoding="utf-8", errors="replace")
            frases = [s.strip().rstrip(".;") for s in re.split(r"(?<=[.;])\s+", re.sub(r"\s+", " ", raw))]
            frases = [s for s in frases if 25 <= len(s) <= 220]
            if frases:
                casos.append(frases)
                total += len(frases)
            if total >= max_frases:
                break
    if not casos:
        print("Aviso: no encontré .txt en --text_dir; uso frases internas.")
        casos = [[s] for s in EVOL_INTERNAS]
        total = len(EVOL_INTERNAS)
    print(f"Casos clínicos: {len(casos)}  |  frases: {total}")
    return casos


# ----------------------------------------------------------------------------- banco de letras
def label_from_dir(name):
    if len(name) == 2 and all(c in "0123456789abcdefABCDEF" for c in name):
        ch = chr(int(name, 16))
        if ch.isalnum():
            return ch
    if len(name) == 1 and name.isalnum():
        return name
    return None


class GlyphBank:
    def __init__(self, root, max_per_char, rng):
        self.paths, self.cache, self.rng = {}, {}, rng
        for d in sorted(Path(root).iterdir()):
            if not d.is_dir():
                continue
            ch = label_from_dir(d.name)
            if ch is None:
                continue
            files = [p for p in d.rglob("*") if p.suffix.lower() in IMG_EXT]
            if files:
                rng.shuffle(files)
                self.paths.setdefault(ch, []).extend(files[:max_per_char])
        if not self.paths:
            raise SystemExit(f"No encontré carpetas de caracteres en {root}. ¿Es la carpeta by_class de SD19?")
        print(f"Caracteres en el banco: {''.join(sorted(self.paths))}  ({len(self.paths)} clases)")

    def has(self, ch):
        return ch in self.paths

    def get(self, ch):
        """Devuelve una máscara recortada (L, tinta=255) de una muestra aleatoria del carácter."""
        p = self.rng.choice(self.paths[ch])
        if p not in self.cache:
            img = ImageOps.invert(Image.open(p).convert("L"))  # SD19: tinta negra sobre blanco
            if np.asarray(img).mean() > 127:  # por si el banco ya viene invertido
                img = ImageOps.invert(img)
            bbox = img.point(lambda v: 255 if v > 100 else 0).getbbox()
            img = img.crop(bbox) if bbox else img
            if len(self.cache) < 60000:
                self.cache[p] = img
            return img
        return self.cache[p]


# ----------------------------------------------------------------------------- estilo por documento
@dataclass
class Style:
    xh: int          # x-height en px
    slant: float     # inclinación (shear)
    thick: int       # -1 fino, 0 normal, 1 grueso
    ink: tuple       # color de tinta
    letter_sp: float
    word_sp: float
    line_gap: float
    jitter: float
    stroke: int      # grosor de trazos dibujados (signos, tildes)


def random_style(rng):
    xh = rng.randint(16, 26)
    ink = rng.choice([(20, 30, 110), (25, 40, 140), (15, 15, 25), (35, 35, 45), (40, 20, 90)])
    return Style(
        xh=xh, slant=rng.uniform(-0.05, 0.3), thick=rng.choice([-1, 0, 0, 1]), ink=ink,
        letter_sp=rng.uniform(-0.04, 0.14), word_sp=rng.uniform(0.55, 1.0), line_gap=rng.uniform(2.5, 3.2),
        jitter=rng.uniform(0.02, 0.08), stroke=max(1, round(xh / 9)),
    )


# ----------------------------------------------------------------------------- render
class Renderer:
    def __init__(self, bank, rng):
        self.bank, self.rng = bank, rng

    def can_render(self, ch):
        if ch == " " or ch in DRAWN_PUNCT:
            return True
        base = ACCENTS.get(ch) or TILDE.get(ch) or DIAER.get(ch) or ch
        return self.bank.has(base)

    def sanitize(self, text):
        text = text.replace("“", "").replace("”", "").replace('"', "").replace("–", "-").replace("—", "-")
        text = text.replace("º", "°").replace("’", "").replace("'", "")
        out = "".join(c if self.can_render(c) else " " for c in text)
        return re.sub(r"\s+", " ", out).strip()

    def _draw_punct(self, ch, st, H, B):
        xh, w = st.xh, st.stroke
        width = {".": 0.35, ",": 0.35, ":": 0.35, ";": 0.35, "-": 0.7, "/": 0.75,
                 "(": 0.45, ")": 0.45, "°": 0.5, "+": 0.8}[ch]
        W = max(4, int(width * xh) + 2 * w)
        im = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(im)
        r = max(1, w)
        cx = W // 2
        def dot(y):
            d.ellipse([cx - r, y - r, cx + r, y + r], fill=255)
        if ch == ".":
            dot(B - r)
        elif ch == ",":
            dot(B - r); d.line([cx + r // 2, B - r, cx - r, B + int(0.35 * xh)], fill=255, width=w)
        elif ch == ":":
            dot(B - r); dot(B - int(0.75 * xh))
        elif ch == ";":
            dot(B - int(0.75 * xh)); dot(B - r); d.line([cx + r // 2, B - r, cx - r, B + int(0.35 * xh)], fill=255, width=w)
        elif ch == "-":
            y = B - int(0.5 * xh); d.line([w, y, W - w, y + self.rng.randint(-1, 1)], fill=255, width=w)
        elif ch == "+":
            y = B - int(0.6 * xh); d.line([w, y, W - w, y], fill=255, width=w); d.line([cx, y - int(0.35 * xh), cx, y + int(0.35 * xh)], fill=255, width=w)
        elif ch == "/":
            d.line([w, B + int(0.1 * xh), W - w, B - int(1.5 * xh)], fill=255, width=w)
        elif ch in "()":
            top, bot = B - int(1.55 * xh), B + int(0.35 * xh)
            box = [w, top, W + int(0.6 * xh), bot] if ch == "(" else [-int(0.6 * xh), top, W - w, bot]
            d.arc(box, 120 if ch == "(" else -60, 240 if ch == "(" else 60, fill=255, width=w)
        elif ch == "°":
            rr = int(0.22 * xh); cy = B - int(1.35 * xh)
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=255, width=max(1, w - 1 + 1))
        return np.asarray(im, dtype=np.uint8)

    def _glyph(self, ch, st, H, B):
        """Devuelve un array (H, W) con el carácter colocado sobre la línea base B."""
        if ch in DRAWN_PUNCT:
            return self._draw_punct(ch, st, H, B)
        base = ACCENTS.get(ch) or TILDE.get(ch) or DIAER.get(ch) or ch
        top, bot = vbox(base)
        s = 1 + self.rng.uniform(-0.08, 0.08)
        gh = max(4, int((bot - top) * st.xh * s))
        g = self.bank.get(base)
        gw = max(3, int(g.width * gh / max(1, g.height)))
        gw = min(gw, int(gh * 1.3))
        g = g.resize((gw, gh), Image.LANCZOS)
        if self.rng.random() < 0.5:
            g = g.rotate(self.rng.uniform(-4, 4), resample=Image.BICUBIC, expand=True)
        if st.thick > 0:
            g = g.filter(ImageFilter.MaxFilter(3))
        elif st.thick < 0 and gh > 20:
            g = g.filter(ImageFilter.MinFilter(3))
        W = g.width
        arr = np.zeros((H, W), dtype=np.uint8)
        y0 = int(B + bot * st.xh * s - g.height + self.rng.uniform(-st.jitter, st.jitter) * st.xh)
        y0 = min(max(0, y0), H - g.height)
        arr[y0:y0 + g.height, :] = np.maximum(arr[y0:y0 + g.height, :], np.asarray(g))
        # diacríticos dibujados encima
        if ch in ACCENTS or ch in TILDE or ch in DIAER:
            im = Image.fromarray(arr)
            d = ImageDraw.Draw(im)
            w = st.stroke
            gtop = y0 + (int(0.25 * st.xh) if base == "i" else 0)
            cx = W // 2
            if ch in ACCENTS:
                d.line([cx - int(0.12 * st.xh), gtop - int(0.15 * st.xh), cx + int(0.2 * st.xh), gtop - int(0.5 * st.xh)], fill=255, width=w)
            elif ch in TILDE:
                y = gtop - int(0.3 * st.xh); a = int(0.35 * st.xh); h = int(0.12 * st.xh)
                d.line([(cx - a, y + h), (cx - a // 3, y - h), (cx + a // 3, y + h), (cx + a, y - h)], fill=255, width=w, joint="curve")
            else:
                r = max(1, w)
                for dx in (-int(0.2 * st.xh), int(0.2 * st.xh)):
                    yy = gtop - int(0.3 * st.xh)
                    d.ellipse([cx + dx - r, yy - r, cx + dx + r, yy + r], fill=255)
            arr = np.asarray(im)
        return arr

    def word(self, text, st):
        """Renderiza una palabra -> (array (H, W), baseline)."""
        H = int(3.4 * st.xh)
        B = int(2.1 * st.xh)
        parts, sp = [], int(st.letter_sp * st.xh)
        for ch in text:
            parts.append(self._glyph(ch, st, H, B))
        total = sum(p.shape[1] for p in parts) + sp * (len(parts) - 1) + 4
        out = np.zeros((H, max(total, 4)), dtype=np.uint8)
        x = 2
        for p in parts:
            x = max(0, x)
            w = min(p.shape[1], out.shape[1] - x)
            if w > 0:
                out[:, x:x + w] = np.maximum(out[:, x:x + w], p[:, :w])
            x += p.shape[1] + sp + self.rng.randint(-1, 1)
        return out, B

    def lines(self, text, st, max_w):
        """Parte el texto en líneas que entren en max_w px. Devuelve [(texto_linea, array)]."""
        words = text.split(" ")
        rendered = [(w, self.word(w, st)[0]) for w in words if w]
        result, cur_t, cur_a = [], [], []
        def flush():
            if cur_a:
                result.append((" ".join(cur_t), self._join(cur_a, st)))
        width = 0
        for w, a in rendered:
            gap = int(st.word_sp * st.xh * self.rng.uniform(0.8, 1.25))
            extra = a.shape[1] + (gap if cur_a else 0)
            if cur_a and width + extra > max_w:
                flush(); cur_t, cur_a, width = [], [], 0
                extra = a.shape[1]
            cur_t.append(w); cur_a.append((a, gap)); width += extra
        flush()
        return result

    def _join(self, items, st):
        H = items[0][0].shape[0]
        W = sum(a.shape[1] for a, _ in items) + sum(g for _, g in items[1:]) + 4
        out = np.zeros((H, W), dtype=np.uint8)
        x = 2
        for i, (a, g) in enumerate(items):
            if i:
                x += g
            out[:, x:x + a.shape[1]] = np.maximum(out[:, x:x + a.shape[1]], a)
            x += a.shape[1]
        # inclinación de toda la línea
        im = Image.fromarray(out)
        s = st.slant
        extra = int(abs(s) * H) + 2
        im = im.transform((W + extra, H), Image.AFFINE,
                          (1, s, -(extra if s > 0 else 0) + s * 0, 0, 1, 0), resample=Image.BICUBIC)
        return np.asarray(im)


# ----------------------------------------------------------------------------- página
def paper(w, h, rng):
    base = np.array(rng.choice([(246, 244, 236), (240, 238, 228), (250, 250, 248), (236, 232, 218)]), dtype=np.float32)
    low = Image.fromarray((np.random.default_rng(rng.randint(0, 1 << 30)).random((12, 9)) * 255).astype(np.uint8))
    low = np.asarray(low.resize((w, h), Image.BICUBIC), dtype=np.float32)[..., None] / 255.0
    fine = np.random.default_rng(rng.randint(0, 1 << 30)).normal(0, 3, (h, w, 1))
    img = base[None, None, :] * (0.97 + 0.035 * low) + fine
    return np.clip(img, 0, 255)


def make_fields(rng, frases, rnd):
    sexo = rng.choice(["M", "F"])
    nombre = f"{rng.choice(NOMBRES_M if sexo == 'M' else NOMBRES_F)} {rng.choice(APELLIDOS)} {rng.choice(APELLIDOS)}"
    dx_name, _, lateral = rng.choice([d for d in DIAGNOSTICOS if d[1] in (None, sexo)])
    dx = dx_name + (rng.choice(LATERALIDAD) if lateral else "") + rng.choice(ESTADIOS)
    if rng.random() < 0.4:
        dx += ", " + rng.choice(COMORB)
    tto = ", ".join(rng.sample(FARMACOS, rng.randint(1, 3))) + rng.choice(CICLOS)
    caso = rng.choice(frases)
    k = rng.randint(2, 5)
    i0 = rng.randint(0, max(0, len(caso) - k))
    evol = ". ".join(abreviar(s, rng) for s in caso[i0:i0 + k])
    if len(evol) > 650:
        evol = evol[:650].rsplit(" ", 1)[0]
    f = {
        "nombre": nombre,
        "hc": str(rng.randint(100000, 9999999)),
        "fecha": f"{rng.randint(1, 28):02d}/{rng.randint(1, 12):02d}/{rng.randint(2015, 2025)}",
        "edad": f"{rng.randint(18, 90)}" + rng.choice(["a", " a", " años"]),
        "sexo": sexo,
        "diagnostico": dx,
        "tratamiento": tto,
        "evolucion": evol,
    }
    return {k: rnd.sanitize(v) for k, v in f.items()}


def compose(fields, rng):
    """Bloques (etiqueta + valor) en orden de escritura."""
    lab = lambda *opts: rng.choice(opts)
    blocks = [
        (lab("Nombre:", "Paciente:", "Pcte:"), fields["nombre"], "nombre"),
        (lab("N° HC:", "HC:", "N° HCl:"), fields["hc"], "hc"),
        (lab("Fecha:", "F:"), fields["fecha"], "fecha"),
        (lab("Edad:",), fields["edad"], "edad"),
        (lab("Sexo:",), fields["sexo"], "sexo"),
        (lab("Dx:", "Diagnóstico:", "DX:"), fields["diagnostico"], "diagnostico"),
        (lab("Tto:", "Tratamiento:", "Rp:"), fields["tratamiento"], "tratamiento"),
        (lab("Evolución:", "Evol:", "Nota:"), fields["evolucion"], "evolucion"),
    ]
    return blocks


def make_page(idx, bank, rnd, frases, rng, W=1240, H=1754):
    st = random_style(rng)
    fields = make_fields(rng, frases, rnd)
    blocks = compose(fields, rng)
    ink = np.zeros((H, W), dtype=np.float32)
    left = rng.randint(70, 140)
    right = W - rng.randint(60, 120)
    y = rng.randint(90, 160)
    step = int(st.line_gap * st.xh)
    line_records = []

    # Encabezado: a veces "Edad" y "Sexo" (y "HC" y "Fecha") van en la misma línea
    merged = []
    i = 0
    while i < len(blocks):
        b = blocks[i]
        if b[2] in ("hc", "edad") and rng.random() < 0.6:
            merged.append([b, blocks[i + 1]]); i += 2
        else:
            merged.append([b]); i += 1

    for group in merged:
        text = "   ".join(f"{l} {v}" for l, v, _ in group)
        indent = left + rng.randint(-6, 6)
        for t, arr in rnd.lines(text, st, right - indent):
            if y + arr.shape[0] >= H - 40:
                break
            h, w = arr.shape
            w = min(w, W - indent)
            region = ink[y:y + h, indent:indent + w]
            np.maximum(region, arr[:, :w].astype(np.float32) / 255.0, out=region)
            ys, xs = np.nonzero(arr[:, :w] > 60)
            if len(ys):
                pad = int(0.35 * st.xh)
                bbox = [max(0, indent + xs.min() - pad), max(0, y + ys.min() - pad),
                        min(W, indent + xs.max() + pad), min(H, y + ys.max() + pad)]
                line_records.append((t, bbox))
            y += step
            indent = left + rng.randint(-6, 6) + (int(0.5 * st.xh) if rng.random() < 0.3 else 0)
        y += int(rng.uniform(0.1, 0.8) * st.xh)
        if y >= H - 60:
            break

    # Composición tinta + papel
    bg = paper(W, H, rng)
    alpha = (ink * rng.uniform(0.82, 1.0))[..., None]
    img = bg * (1 - alpha) + np.array(st.ink, dtype=np.float32)[None, None, :] * alpha
    page = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

    # Degradación tipo escaneo / foto
    if rng.random() < 0.7:
        page = page.filter(ImageFilter.GaussianBlur(rng.uniform(0.2, 0.9)))
    if rng.random() < 0.3:
        f = rng.uniform(0.6, 0.85)
        page = page.resize((int(W * f), int(H * f)), Image.BILINEAR).resize((W, H), Image.BILINEAR)
    page_text = "\n".join(t for t, _ in line_records)
    return page, page_text, fields, line_records


def save_jpeg(img, path, rng):
    img.save(path, quality=rng.randint(60, 95))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--char_root", required=True, type=Path, help="Carpeta by_class de SD19 (o una carpeta por carácter)")
    ap.add_argument("--text_dir", type=Path, default=None, help="Carpeta con .txt clínicos (SPACCC)")
    ap.add_argument("--out_dir", type=Path, default=Path("synth"))
    ap.add_argument("--n", type=int, default=100, help="Número de páginas")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max_per_char", type=int, default=3000, help="Máx. muestras por carácter a indexar")
    ap.add_argument("--start_id", type=int, default=0)
    ap.add_argument("--preview", action="store_true")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    bank = GlyphBank(args.char_root, args.max_per_char, rng)
    rnd = Renderer(bank, rng)
    frases = cargar_frases(args.text_dir, rng)

    (args.out_dir / "pages").mkdir(parents=True, exist_ok=True)
    (args.out_dir / "lines").mkdir(parents=True, exist_ok=True)
    fp = open(args.out_dir / "pages.jsonl", "a", encoding="utf-8")
    fl = open(args.out_dir / "lines.jsonl", "a", encoding="utf-8")
    preview = []

    for k in range(args.start_id, args.start_id + args.n):
        pid = f"hc_{k:05d}"
        for _ in range(5):  # si la página se cortó y algún campo no entró, se regenera
            page, text, fields, recs = make_page(k, bank, rnd, frases, rng)
            flat = text.replace("\n", " ")
            if all(v in flat for v in fields.values()):
                break
        ppath = args.out_dir / "pages" / f"{pid}.jpg"
        save_jpeg(page, ppath, rng)
        fp.write(json.dumps({"id": pid, "image": str(ppath.resolve()), "text": text, "fields": fields}, ensure_ascii=False) + "\n")
        for j, (t, bbox) in enumerate(recs):
            lid = f"{pid}_{j:02d}"
            crop = page.crop(bbox)
            lpath = args.out_dir / "lines" / f"{lid}.png"
            crop.save(lpath)
            fl.write(json.dumps({"id": lid, "image": str(lpath.resolve()), "text": t}, ensure_ascii=False) + "\n")
            if args.preview and len(preview) < 12:
                preview.append(crop)
        if (k - args.start_id + 1) % 50 == 0:
            print(f"{k - args.start_id + 1}/{args.n} páginas")
    fp.close(); fl.close()

    if preview:
        w = max(p.width for p in preview); h = sum(p.height + 6 for p in preview)
        mosaic = Image.new("RGB", (w, h), "white"); y = 0
        for p in preview:
            mosaic.paste(p, (0, y)); y += p.height + 6
        mosaic.save(args.out_dir / "preview_lines.png")
    print(f"Listo: {args.n} páginas en {args.out_dir}/pages, líneas en {args.out_dir}/lines.jsonl")


if __name__ == "__main__":
    main()
