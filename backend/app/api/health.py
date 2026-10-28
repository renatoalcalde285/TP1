from fastapi import APIRouter
from sqlalchemy import text
from app.core.storage import s3_client

from app.core.database import engine

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "inen-api"
    }

@router.get("/health/db")
async def db_health():

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {
            "database": "connected"
        }

    except Exception as e:
        return {
            "database": "error",
            "detail": str(e)
        }

@router.get("/health/storage")
async def storage_health():

    try:
        s3_client.list_buckets()

        return {
            "storage": "connected"
        }

    except Exception as e:
        return {
            "storage": "error",
            "detail": str(e)
        }