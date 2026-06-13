from fastapi import APIRouter, Query

from app.schemas.carriers import CarrierVerifyResponse
from app.services.fmcsa import verify_carrier

router = APIRouter(prefix="/carriers", tags=["carriers"])


@router.get("/verify-mc", response_model=CarrierVerifyResponse)
async def verify_mc(mc_number: str = Query(...)):
    return await verify_carrier(mc_number)
