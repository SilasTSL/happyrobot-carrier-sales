import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
logging.basicConfig(level=logging.INFO)

from app.auth import require_api_key
from app.database import Base, SessionLocal, engine
from app.database.seed import seed_all
from app.routers import call_records, carriers, loads, metrics
from app.routers import auth_router
from app.routers.dashboard import router as dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Drop and recreate all tables on startup so schema changes always apply.
    # All data is seeded, so this is safe for this demo.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_all(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="HappyRobot Carrier Sales",
    lifespan=lifespan,
    dependencies=[Depends(require_api_key)],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Existing carrier-sales endpoints (API-key protected via global dependency)
app.include_router(loads.router)
app.include_router(call_records.router)
app.include_router(carriers.router)
app.include_router(metrics.router)

# Dashboard endpoints — JWT auth handled per-route via get_current_company
app.include_router(auth_router.router)
app.include_router(dashboard_router)


@app.get("/health")
def health():
    return {"status": "ok"}
