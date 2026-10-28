# TP1 - Procesamiento de Actas mediante Inteligencia Artificial

## Descripción

Este repositorio contiene el avance actual del proyecto de procesamiento y transcripción de actas utilizando inteligencia artificial.

La arquitectura se encuentra dividida en tres componentes principales:

- Frontend desarrollado en React + TypeScript.
- Backend desarrollado en FastAPI y desplegado mediante Docker.
- Servicio de inferencia basado en Qwen2.5-VL desplegado en una máquina virtual Linux independiente.

## Arquitectura General

```text
Frontend (React)

        ↓

Backend (FastAPI + Docker)

        ↓

Servicio de Inferencia (Qwen2.5-VL)

        ↓

Transcripción de documentos
```

## Estado actual del proyecto

Actualmente se encuentran implementados los siguientes componentes:

- Autenticación mediante JWT.
- Gestión de usuarios.
- Carga de documentos.
- Procesamiento asíncrono mediante Celery.
- Persistencia de información mediante PostgreSQL.
- Almacenamiento de archivos mediante RustFS.
- Comunicación entre Backend y Servicio de Inferencia.
- Servicio de inferencia utilizando Qwen2.5-VL.
- Interfaz web para autenticación y carga de documentos.

## Estructura del repositorio

```text
TP1
│
├── backend
├── frontend
├── vm
│   └── notebooks
│
└── docker-compose.yml
```

### backend

Contiene la API principal desarrollada con FastAPI.

Incluye:

- Autenticación JWT.
- Gestión de documentos.
- Modelos de base de datos.
- Integración con PostgreSQL.
- Integración con Redis.
- Integración con RustFS.
- Procesamiento asíncrono mediante Celery.

### frontend

Contiene la aplicación web desarrollada en React + TypeScript.

Incluye actualmente:

- Login.
- Carga de documentos.
- Página de procesamiento.
- Integración con la API del backend.

### vm

Contiene los archivos correspondientes al servicio de inferencia desplegado en una máquina virtual Linux.

#### Servicio de Inferencia

Archivos utilizados actualmente por el servicio:

```text
app.py
model_service.py
prompts.py
requirements.txt
```

Su responsabilidad es:

- Cargar el modelo Qwen2.5-VL.
- Recibir imágenes enviadas por el backend.
- Ejecutar la inferencia.
- Devolver la transcripción obtenida.

#### Notebook Experimental

La carpeta:

```text
vm/notebooks/
```

contiene el archivo:

```text
modelo.ipynb
```

Este corresponde al notebook original utilizado durante la fase experimental del proyecto.

Incluye:

- Configuración inicial del modelo.
- Pruebas de inferencia.
- Experimentación con prompts.
- Validaciones realizadas durante el desarrollo.

El notebook se conserva únicamente con fines académicos y para evidenciar el proceso de investigación y experimentación realizado durante el proyecto.

## Levantar el Backend

Desde la raíz del proyecto:

```bash
docker compose up -d
```

Esto iniciará:

- PostgreSQL
- PgAdmin
- Redis
- RustFS
- Backend FastAPI
- Celery Worker

## Levantar el Frontend

```bash
cd frontend
npm install
npm run dev
```

## Levantar el Servicio de Inferencia

Dentro de la máquina virtual Linux:

```bash
cd ~/qwen-server

source venv/bin/activate

uvicorn app:app --host 0.0.0.0 --port 7860
```

### Verificar funcionamiento

```bash
curl http://localhost:7860/ping
```

Respuesta esperada:

```json
{
  "status": "ok"
}
```

## Observaciones

Los pesos del modelo Qwen2.5-VL no se encuentran incluidos dentro de este repositorio debido a su tamaño.

Durante el despliegue del servicio de inferencia deben descargarse desde Hugging Face utilizando las dependencias incluidas en `requirements.txt`.

## Estado del avance

El repositorio refleja el estado actual de la arquitectura del sistema:

- Frontend funcional.
- Backend funcional.
- Infraestructura Docker funcional.
- Servicio de inferencia funcional en máquina virtual.
- Integración Backend ↔ Servicio de Inferencia implementada.
- Fase actual orientada a integración, validación y mejora del procesamiento documental.