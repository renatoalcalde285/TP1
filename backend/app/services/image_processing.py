import cv2
import numpy as np

from PIL import Image


MAX_PIXELS = 2500 * 28 * 28


def upscale_lanczos_cv2(img, factor=2):

    h, w = img.shape[:2]

    return cv2.resize(
        img,
        (w * factor, h * factor),
        interpolation=cv2.INTER_LANCZOS4
    )


def clahe_filter(img):

    lab = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2LAB
    )

    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=3.0,
        tileGridSize=(8, 8)
    )

    return cv2.cvtColor(
        cv2.merge(
            [
                clahe.apply(l),
                a,
                b
            ]
        ),
        cv2.COLOR_LAB2BGR
    )


def sharpen_filter(img):

    kernel = np.array(
        [
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ],
        dtype=np.float32
    )

    return cv2.addWeighted(
        img,
        0.4,
        cv2.filter2D(
            img,
            -1,
            kernel
        ),
        0.6,
        0
    )


def preprocess_document(
    image: Image.Image,
    filtros_baja_res: bool = True
):

    w, h = image.size

    pixels = w * h

    print(
        f"[FILTROS] Resolución original: {w}x{h}"
    )

    arr = cv2.cvtColor(
        np.array(image),
        cv2.COLOR_RGB2BGR
    )

    # ==========================================
    # Solo aplicar Lanczos si la imagen es pequeña
    # ==========================================

    if pixels < MAX_PIXELS and filtros_baja_res:

        print(
            "[FILTROS] Aplicando escalado Lanczos"
        )

        factor = (
            MAX_PIXELS / pixels
        ) ** 0.5

        nuevo_w = int(w * factor)
        nuevo_h = int(h * factor)

        arr = cv2.resize(
            arr,
            (
                nuevo_w,
                nuevo_h
            ),
            interpolation=cv2.INTER_LANCZOS4
        )

        print(
            f"[FILTROS] Nueva resolución: {nuevo_w}x{nuevo_h}"
        )

    else:

        print(
            "[FILTROS] Se conserva resolución original"
        )

    # ==========================================
    # CLAHE SIEMPRE
    # ==========================================

    arr = clahe_filter(arr)

    print(
        "[FILTROS] CLAHE aplicado"
    )

    # ==========================================
    # SHARPEN SIEMPRE
    # ==========================================

    arr = sharpen_filter(arr)

    print(
        "[FILTROS] Sharpen aplicado"
    )

    resultado = Image.fromarray(
        cv2.cvtColor(
            arr,
            cv2.COLOR_BGR2RGB
        )
    )

    print(
        f"[FILTROS] Resolución final: "
        f"{resultado.size[0]}x{resultado.size[1]}"
    )

    return resultado