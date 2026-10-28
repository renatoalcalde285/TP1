# VM - Servicio de Inferencia con Qwen2.5-VL

Esta carpeta contiene los componentes desplegados en una máquina virtual Linux utilizados para la inferencia de documentos mediante el modelo multimodal Qwen2.5-VL.

La arquitectura del proyecto se encuentra dividida en tres componentes principales:

1. Frontend (React).
2. Backend (FastAPI desplegado mediante Docker).
3. Servicio de inferencia ubicado en una máquina virtual independiente.

El backend se comunica con este servicio mediante solicitudes HTTP para realizar el procesamiento de imágenes y obtener la transcripción generada por el modelo.

## Contenido

### app.py

Servidor FastAPI que expone los endpoints utilizados por el backend para comunicarse con el modelo de inferencia.

### model_service.py

Contiene la lógica de carga del modelo Qwen2.5-VL y la ejecución del proceso de inferencia sobre imágenes recibidas por la API.

### prompts.py

Define los prompts utilizados durante la transcripción de documentos.

### requirements.txt

Dependencias necesarias para ejecutar el servicio en la máquina virtual.

## Carpeta notebooks

La carpeta `notebooks` contiene el notebook original utilizado durante la fase experimental del proyecto.

Este notebook fue proporcionado como base para las pruebas y contiene:

- Configuración inicial del modelo.
- Experimentos de inferencia.
- Pruebas de prompts.
- Evaluaciones realizadas durante el desarrollo.

El notebook se incluye únicamente con fines de documentación y trazabilidad del proyecto.

## Observación

Los pesos del modelo Qwen2.5-VL no se encuentran incluidos en este repositorio debido a su tamaño. Durante el despliegue deben descargarse desde Hugging Face utilizando las herramientas correspondientes.