import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()
logging.basicConfig(level=logging.INFO)

from app.database import Base, SessionLocal, engine
from app.database.seed import seed_call_records, seed_loads
from app.routers import call_records, carriers, loads, metrics


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
app.include_router(carriers.router)
app.include_router(metrics.router)


@app.get("/health")
def health():
    return {"status": "ok"}
