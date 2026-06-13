import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)

from app.database import Base, SessionLocal, engine
from app.database.seed import seed_call_records, seed_loads
from app.routers import call_records, loads


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_loads(db)
        seed_call_records(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Acme Logistics — Inbound Carrier Sales", lifespan=lifespan)

app.include_router(loads.router)
app.include_router(call_records.router)


@app.get("/health")
def health():
    return {"status": "ok"}
