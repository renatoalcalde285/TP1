from pydantic import BaseModel


class UploadResponse(BaseModel):

    id_documento: int

    id_archivo: int

    nombre_archivo: str

    ruta_almacenamiento: str

    estado: str