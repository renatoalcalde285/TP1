import time
import cv2
import numpy as np
import torch
import json
import re

from PIL import Image

from transformers import (
    AutoProcessor,
    BitsAndBytesConfig,
    Qwen2_5_VLForConditionalGeneration
)

from qwen_vl_utils import process_vision_info

from prompts import (
    PROMPT,
    PROMPT_EXTRACT
)


MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"

print("Cargando modelo...")


bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)


processor = AutoProcessor.from_pretrained(
    MODEL_ID,
    min_pixels=256 * 28 * 28,
    max_pixels=2500 * 28 * 28,
)


model = (
    Qwen2_5_VLForConditionalGeneration
    .from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto"
    )
)

model.eval()

print("Modelo cargado correctamente")


MAX_PIXELS = 2500 * 28 * 28


def _clahe(img):

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


def _sharp(img):

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


def preprocesar(
    img,
    filtros_baja_res=True
):

    w, h = img.size

    pixeles = w * h

    if pixeles >= MAX_PIXELS:

        print(
            f"Imagen buena calidad: {w}x{h}"
        )

        return img

    if filtros_baja_res:

        print(
            f"Mejorando imagen: {w}x{h}"
        )

        arr = cv2.cvtColor(
            np.array(img),
            cv2.COLOR_RGB2BGR
        )

        factor = (
            MAX_PIXELS / pixeles
        ) ** 0.5

        arr = cv2.resize(
            arr,
            (
                int(w * factor),
                int(h * factor)
            ),
            interpolation=cv2.INTER_LANCZOS4
        )

        arr = _clahe(arr)

        arr = _sharp(arr)

        return Image.fromarray(
            cv2.cvtColor(
                arr,
                cv2.COLOR_BGR2RGB
            )
        )

    return img


def transcribir_acta(
    image: Image.Image
):

    print("\n" + "=" * 60)
    print("INICIO TRANSCRIPCION")
    print("=" * 60)

    inicio_total = time.time()

    image = preprocesar(image)

    print(
        f"Resolucion final: {image.size}"
    )

    test_inputs = processor(
        text=[
            "<|vision_start|><|image_pad|><|vision_end|>"
        ],
        images=[image],
        return_tensors="pt"
    )

    print(
        f"Keys disponibles: {list(test_inputs.keys())}"
    )

    if "image_grid_thw" in test_inputs:

        t, h, w = (
            test_inputs["image_grid_thw"][0]
            .tolist()
        )

        print(
            f"IMAGE_GRID_THW: {test_inputs['image_grid_thw']}"
        )

        print(
            f"GRID VISUAL: {h}x{w}"
        )

        print(
            f"TOKENS VISUALES: {h * w // 4}"
        )

    else:

        print(
            "NO EXISTE image_grid_thw"
        )

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": image
                },
                {
                    "type": "text",
                    "text": PROMPT
                }
            ]
        }
    ]

    text = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    img_inputs, vid_inputs = (
        process_vision_info(messages)
    )

    inputs = processor(
        text=[text],
        images=img_inputs,
        videos=vid_inputs,
        padding=True,
        return_tensors="pt"
    )

    inputs = {
        k: v.to(model.device)
        for k, v in inputs.items()
    }

    print("ENTRANDO A GENERATE")

    inicio_generate = time.time()

    with torch.no_grad():

        output_ids = model.generate(
            **inputs,
            max_new_tokens=64,
            do_sample=False,
            repetition_penalty=1.05
        )

    tiempo_generate = round(
        time.time() - inicio_generate,
        2
    )

    print(
        f"TIEMPO GENERACION: {tiempo_generate} segundos"
    )

    print("SALIENDO DE GENERATE")

    generated_ids = [
        output_ids[i][
            len(inputs["input_ids"][i]):
        ]
        for i in range(len(output_ids))
    ]

    resultado = processor.batch_decode(
        generated_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False
    )[0]

    tiempo_total = round(
        time.time() - inicio_total,
        2
    )

    print(
        f"TIEMPO TOTAL: {tiempo_total} segundos"
    )

    print("=" * 60)
    print("FIN TRANSCRIPCION")
    print("=" * 60)

    return resultado, tiempo_total

def extraer_campos_texto(
    texto_documento: str
):

    prompt = f"""
{PROMPT_EXTRACT}

TEXTO:

{texto_documento}
"""

    inputs = processor.tokenizer(
        prompt,
        return_tensors="pt"
    )

    inputs = {
        k: v.to(model.device)
        for k, v in inputs.items()
    }

    with torch.no_grad():

        output_ids = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=False
        )

        generated_ids = output_ids[
            0,
            inputs["input_ids"].shape[1]:
        ]

        respuesta = processor.tokenizer.decode(
            generated_ids,
            skip_special_tokens=True
        )

    try:

        matches = re.findall(
            r"```json\s*(\{.*?\})\s*```",
            respuesta,
            re.DOTALL
        )
        if len(matches) == 0:
            raise Exception(
                "No se encontró J*ON"
            )

        json_text = matches[0]

        return json.loads(json_text)

    except Exception as e:

        print(
            f"Error parseando JSON: {e}"
    )

        return {
            "error": "No se pudo generar JSON"
        }