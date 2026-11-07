import io

from PIL import Image

from fastapi import (
    FastAPI,
    UploadFile,
    File
)

from model_service import (
    transcribir_acta,
    extraer_campos_texto
)

from pydantic import BaseModel

class ExtractionRequest(BaseModel):
    texto: str


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

@app.post("/extraer-campos")
def extraer_campos(
    request: ExtractionRequest
):

    resultado = extraer_campos_texto(
        request.texto
    )

    return resultado