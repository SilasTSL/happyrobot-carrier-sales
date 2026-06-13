import logging
import os
import re

import httpx

from app.schemas.carriers import CarrierVerifyResponse

logger = logging.getLogger(__name__)

_FMCSA_BASE = "https://mobile.fmcsa.dot.gov/qc/services/carriers"


def _clean_mc(mc_number: str) -> str:
    return re.sub(r"\D", "", mc_number)


def _is_eligible(carrier: dict) -> bool:
    if carrier.get("allowedToOperate") != "Y":
        return False
    if carrier.get("statusCode") != "A":
        return False
    return (
        carrier.get("commonAuthorityStatus") == "A"
        or carrier.get("contractAuthorityStatus") == "A"
    )


async def verify_carrier(mc_number: str) -> CarrierVerifyResponse:
    api_key = os.environ.get("FMCSA_API_KEY")
    if not api_key:
        logger.error("FMCSA_API_KEY is not configured — rejecting verification request")
        return CarrierVerifyResponse(verified=False, carrier_name=None, dot_number=None)

    clean_mc = _clean_mc(mc_number)
    url = f"{_FMCSA_BASE}/docket-number/{clean_mc}"
    logger.info("Verifying MC raw=%s cleaned=%s url=%s", mc_number, clean_mc, url)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params={"webKey": api_key})
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error("FMCSA API request failed for MC %s: %s", mc_number, exc)
        return CarrierVerifyResponse(verified=False, carrier_name=None, dot_number=None)

    data = response.json()
    logger.info("Raw FMCSA content for MC %s: %s", clean_mc, data.get("content"))

    carriers = [
        item["carrier"]
        for item in (response.json().get("content") or [])
        if "carrier" in item
    ]

    logger.info("FMCSA returned %d carrier record(s) for MC %s", len(carriers), mc_number)

    for carrier in carriers:
        if _is_eligible(carrier):
            name = carrier.get("legalName") or carrier.get("dbaName")
            dot = carrier.get("dotNumber")
            logger.info("MC %s verified — carrier: %s, DOT: %s", mc_number, name, dot)
            return CarrierVerifyResponse(verified=True, carrier_name=name, dot_number=dot)

    logger.info("MC %s did not pass eligibility checks", mc_number)
    return CarrierVerifyResponse(verified=False, carrier_name=None, dot_number=None)
