import io

from PIL import Image

from fastapi import (
    FastAPI,
    UploadFile,
    File
)

from model_service import (
    transcribir_acta
)

app = FastAPI(
    title="INEN Qwen Server"
)


@app.get("/ping")
def ping():

    return {
        "status": "ok"
    }


@app.post("/transcribir")
async def transcribir(
    file: UploadFile = File(...)
):

    print("PETICION RECIBIDA")

    image = Image.open(
        io.BytesIO(
            await file.read()
        )
    ).convert("RGB")

    texto, tiempo = (
        transcribir_acta(image)
    )

    return {
        "texto": texto,
        "tiempo_segundos": tiempo
    }