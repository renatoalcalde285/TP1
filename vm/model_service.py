import time
import torch

from PIL import Image

from transformers import (
    AutoProcessor,
    BitsAndBytesConfig,
    Qwen2_5_VLForConditionalGeneration
)

from prompts import PROMPT


MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"

print("Cargando modelo...")

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

processor = AutoProcessor.from_pretrained(
    MODEL_ID
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


def transcribir_acta(
    image: Image.Image
):

    print("\n" + "=" * 50)
    print("INICIO TRANSCRIPCION")
    print("=" * 50)

    inicio_total = time.time()

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

    print("PROCESANDO IMAGEN")

    inputs = processor(
        text=[text],
        images=[image],
        return_tensors="pt"
    )

    inputs = {
        k: v.to(model.device)
        for k, v in inputs.items()
    }

    print("GENERANDO RESPUESTA")

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
        output_ids[i][len(inputs["input_ids"][i]):]
        for i in range(len(output_ids))
    ]

    resultado = processor.batch_decode(
        generated_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0]

    tiempo_total = round(
        time.time() - inicio_total,
        2
    )

    print("RESPUESTA GENERADA")

    print(
        f"TIEMPO TOTAL: {tiempo_total} segundos"
    )

    print("=" * 50)
    print("FIN TRANSCRIPCION")
    print("=" * 50 + "\n")

    return resultado, tiempo_total