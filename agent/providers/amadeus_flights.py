import os
import time
import requests
from datetime import datetime, timedelta

AMADEUS_BASE = os.getenv("AMADEUS_BASE", "https://test.api.amadeus.com")
CLIENT_ID = os.getenv("AMADEUS_API_KEY")
CLIENT_SECRET = os.getenv("AMADEUS_API_SECRET")

_TOKEN = {"value": None, "exp": 0}

def _token():
    # Reuse token until ~60s before expiry
    if _TOKEN["value"] and time.time() < _TOKEN["exp"] - 60:
        return _TOKEN["value"]
    resp = requests.post(
        f"{AMADEUS_BASE}/v1/security/oauth2/token",
        data={"grant_type": "client_credentials",
              "client_id": CLIENT_ID,
              "client_secret": CLIENT_SECRET},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    _TOKEN["value"] = data["access_token"]
    _TOKEN["exp"] = time.time() + int(data["expires_in"])
    return _TOKEN["value"]

def _fmt_date(d: str) -> str:
    # accept YYYY-MM-DD; pass through
    return d

def _compute_return(start_iso: str, nights: int) -> str:
    y, m, d = map(int, start_iso.split("-"))
    dt = datetime(y, m, d) + timedelta(days=int(nights))
    return dt.date().isoformat()

def search_roundtrip(params: dict) -> list[dict]:
    """
    Minimal round-trip search using Amadeus Flight Offers Search v2.
    Params expected:
      origin (IATA), destination (IATA), startDate (YYYY-MM-DD), nights (int),
      adults (int), children (int), currency (e.g., GBP)
    """
    if not (CLIENT_ID and CLIENT_SECRET):
        print("[Amadeus/Flights] Missing credentials.")
        return []

    origin = (params.get("origin") or "EMA").upper()
    dest = (params.get("destination") or "ALC").upper()
    start = _fmt_date(params.get("startDate") or datetime.utcnow().date().isoformat())
    nights = int(params.get("nights", 4))
    ret = _compute_return(start, nights)
    adults = int(params.get("adults", 2))
    children = int(params.get("children", 0))
    currency = params.get("currency", "GBP").upper()
    max_results = int(params.get("limit", 10))

    tk = _token()
    headers = {"Authorization": f"Bearer {tk}"}

    q = {
        "originLocationCode": origin,
        "destinationLocationCode": dest,
        "departureDate": start,
        "returnDate": ret,
        "adults": adults,
        "currencyCode": currency,
        "max": max_results
    }
    if children:
        q["children"] = children

    try:
        r = requests.get(f"{AMADEUS_BASE}/v2/shopping/flight-offers",
                         headers=headers, params=q, timeout=20)
        if r.status_code == 401:
            # refresh once
            _TOKEN["value"] = None
            headers["Authorization"] = f"Bearer {_token()}"
            r = requests.get(f"{AMADEUS_BASE}/v2/shopping/flight-offers",
                             headers=headers, params=q, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"[Amadeus/Flights] API error: {e}")
        return []

    payload = r.json()
    data = payload.get("data", [])

    results = []
    dic = {d["id"]: d for d in payload.get("dictionaries", {}).get("carriers", {}).items()}  # not used but placeholder

    for offer in data:
        price = offer.get("price", {}).get("grandTotal")
        itineraries = offer.get("itineraries", [])
        dep, arr, carrier = None, None, None
        if itineraries:
            out = itineraries[0].get("segments", [])
            back = itineraries[-1].get("segments", [])
            first = out[0] if out else None
            last = back[-1] if back else (out[-1] if out else None)
            dep = first.get("departure", {}).get("at") if first else None
            arr = last.get("arrival", {}).get("at") if last else None
            carrier = (first.get("carrierCode") if first else None) or "?"
        results.append({
            "provider": "Amadeus Flights",
            "price": float(price) if price else None,
            "carrier": carrier,
            "departure": dep,
            "arrival": arr,
            "raw": offer  # keep raw for later enrichment (fare families, bags)
        })
    return results
