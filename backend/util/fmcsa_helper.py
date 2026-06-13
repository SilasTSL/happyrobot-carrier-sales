"""
find_valid_mc.py

Find valid, ACTIVE, AUTHORIZED MC (docket) numbers from the FMCSA QCMobile API.

There is no "list all MC numbers" endpoint, so we work backwards:
    1. Search carriers by name           -> get DOT numbers of real carriers
    2. Filter to active + authorized      -> keep only good ones
    3. GET /carriers/{dot}/docket-numbers -> pull their real MC number(s)
    4. GET /carriers/docket-number/{mc}   -> confirm the MC resolves correctly
                                             (this is the route the agent uses)

Usage:
    export FMCSA_WEB_KEY=your_key_here
    python find_valid_mc.py

Notes:
    - Run this from a US IP / US-hosted environment. FMCSA appears to geo-block
      non-US traffic with a 403.
    - Replace the CANDIDATE_NAMES with whatever carriers you want to harvest.
"""

import os
import sys
import time
import requests

BASE = "https://mobile.fmcsa.dot.gov/qc/services"

# Large, established for-hire freight carriers likely to be active + authorized.
# Tweak freely. (Greyhound is included only as a known-good sanity check.)
CANDIDATE_NAMES = [
    "schneider",
    "j b hunt",
    "werner",
    "old dominion",
    "estes",
    "saia",
]

WEB_KEY = os.environ.get("FMCSA_API_KEY")
if not WEB_KEY:
    sys.exit("Set FMCSA_API_KEY in your environment first.")


def _get(path: str, **params) -> dict | None:
    """GET a QCMobile path, return parsed JSON or None on any failure."""
    params["webKey"] = WEB_KEY
    try:
        r = requests.get(f"{BASE}{path}", params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print(f"  ! request failed for {path}: {e}")
        return None
    except ValueError:
        print(f"  ! non-JSON response for {path}")
        return None


def is_active_and_authorized(carrier: dict) -> bool:
    """Broker-style eligibility: allowed to operate, active, with for-hire authority."""
    allowed = carrier.get("allowedToOperate") == "Y"
    active = carrier.get("statusCode") == "A"
    has_authority = (
        carrier.get("commonAuthorityStatus") == "A"
        or carrier.get("contractAuthorityStatus") == "A"
    )
    return allowed and active and has_authority


def search_by_name(name: str) -> list[dict]:
    data = _get(f"/carriers/name/{name}")
    if not data:
        return []
    content = data.get("content") or []
    # each item -> {"carrier": {...}, "_links": {...}}
    return [item.get("carrier", {}) for item in content if isinstance(item, dict)]


def get_mc_numbers(dot_number: int) -> list[str]:
    """Pull MC docket number(s) for a DOT number."""
    data = _get(f"/carriers/{dot_number}/docket-numbers")
    if not data:
        return []
    content = data.get("content") or []
    mcs = []
    for item in content:
        # docket-numbers content items typically expose a docket/prefix field.
        # Shapes vary, so grab whatever digit field is present.
        if isinstance(item, dict):
            # common keys seen: "docketNumber", "docket", "prefix"+number
            val = item.get("docketNumber") or item.get("docket")
            if val:
                mcs.append(str(val))
    return mcs


def verify_mc(mc: str) -> dict | None:
    """Run the MC back through the docket-number route (the agent's route)."""
    data = _get(f"/carriers/docket-number/{mc}")
    if not data:
        return None
    content = data.get("content") or []
    if not content:
        return None
    return content[0].get("carrier", {})


def main():
    found = []
    for name in CANDIDATE_NAMES:
        print(f"\n=== searching: {name} ===")
        carriers = search_by_name(name)
        if not carriers:
            print("  (no results)")
            continue

        for c in carriers:
            dot = c.get("dotNumber")
            legal = c.get("legalName")
            if not is_active_and_authorized(c):
                continue
            print(f"  + active/authorized: {legal} (DOT {dot})")

            for mc in get_mc_numbers(dot):
                confirmed = verify_mc(mc)
                time.sleep(0.3)  # be polite to the API
                if confirmed and is_active_and_authorized(confirmed):
                    print(f"      -> VALID MC {mc} resolves to "
                          f"{confirmed.get('legalName')} (active+authorized)")
                    found.append({
                        "mc_number": mc,
                        "dot_number": dot,
                        "legal_name": confirmed.get("legalName"),
                    })
                else:
                    print(f"      -> MC {mc} did NOT confirm as active/authorized")
            time.sleep(0.3)

    print("\n================ VALID TEST MC NUMBERS ================")
    if not found:
        print("None found — try different / larger carrier names.")
    for f in found:
        print(f"  MC {f['mc_number']:>10}  DOT {f['dot_number']:>10}  {f['legal_name']}")


if __name__ == "__main__":
    main()