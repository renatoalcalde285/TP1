from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.storage import ensure_bucket
from app.core.database import create_tables
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):

    ensure_bucket()

    #create_tables()


    yield


app = FastAPI(
    title="INEN API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)