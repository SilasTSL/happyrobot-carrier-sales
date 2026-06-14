from fastapi import APIRouter

from app.routers.dashboard import breakdowns, calls, summary, timeseries

router = APIRouter(prefix="/api", tags=["dashboard"])
router.include_router(summary.router)
router.include_router(timeseries.router)
router.include_router(breakdowns.router)
router.include_router(calls.router)
