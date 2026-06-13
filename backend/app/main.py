from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
import app.models  # noqa: F401 — registers models with Base metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Acme Logistics — Inbound Carrier Sales", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}
