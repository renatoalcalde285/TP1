from pydantic import BaseModel

class DocumentValidationRequest(BaseModel):

    datos_estructurados: dict