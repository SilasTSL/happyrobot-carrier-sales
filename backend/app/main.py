import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)

from app.database import Base, SessionLocal, engine
from app.seed import seed_loads
from app.routers import loads
import app.models  # noqa: F401 — registers models with Base metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_loads(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Acme Logistics — Inbound Carrier Sales", lifespan=lifespan)

app.include_router(loads.router)


@app.get("/health")
def health():
    return {"status": "ok"}
