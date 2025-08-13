import os
import time
import requests
from datetime import datetime, timedelta

AMADEUS_BASE = os.getenv("AMADEUS_BASE", "https://test.api.amadeus.com")
CLIENT_ID = os.getenv("AMADEUS_API_KEY")
CLIENT_SECRET = os.getenv("AMADEUS_API_SECRET")

_TOKEN = {"value": None, "exp": 0}

def _token():
    if _TOKEN["value"] and time.time() < _TOKEN["exp"] - 60:
        return _TOKEN["value"]
    r = requests.post(
        f"{AMADEUS_BASE}/v1/security/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    _TOKEN["value"] = data["access_token"]
    _TOKEN["exp"] = time.time() + int(data.get("expires_in", 1800))
    return _TOKEN["value"]

def _return_date(start_iso: str, nights: int) -> str:
    y, m, d = map(int, start_iso.split("-"))
    return (datetime(y, m, d) + timedelta(days=int(nights))).date().isoformat()

def search_roundtrip(params: dict) -> list[dict]:
    """
    Amadeus Flight Offers Search v2 (round-trip).
    Required: origin(IATA), destination(IATA), startDate(YYYY-MM-DD), nights(int)
    Optional: adults, children, currency(GBP), limit(max results)
    """
    if not (CLIENT_ID and CLIENT_SECRET):
        print("[Amadeus/Flights] Missing credentials.")
        return []

    origin = (params.get("origin") or "EMA").upper()
    dest = (params.get("destination") or "ALC").upper()
    start = params.get("startDate")
    if not start:
        start = datetime.utcnow().date().isoformat()
    nights = int(params.get("nights", 4))
    ret = _return_date(start, nights)
    adults = int(params.get("adults", 2))
    children = int(params.get("children", 0))
    currency = (params.get("currency") or "GBP").upper()
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
        "max": max_results,
    }
    if children:
        q["children"] = children

    r = requests.get(
        f"{AMADEUS_BASE}/v2/shopping/flight-offers", headers=headers, params=q, timeout=25
    )
    if r.status_code == 401:
        _TOKEN["value"] = None
        headers["Authorization"] = f"Bearer {_token()}"
        r = requests.get(
            f"{AMADEUS_BASE}/v2/shopping/flight-offers", headers=headers, params=q, timeout=25
        )
    r.raise_for_status()
    payload = r.json()
    data = payload.get("data", [])

    out = []
    for offer in data:
        price = offer.get("price", {}).get("grandTotal")
        itineraries = offer.get("itineraries", [])
        dep, arr, carrier = None, None, None
        if itineraries:
            out_seg = itineraries[0].get("segments", [])
            back_seg = itineraries[-1].get("segments", [])
            first = out_seg[0] if out_seg else None
            last = back_seg[-1] if back_seg else (out_seg[-1] if out_seg else None)
            dep = first.get("departure", {}).get("at") if first else None
            arr = last.get("arrival", {}).get("at") if last else None
            carrier = (first.get("carrierCode") if first else None) or "?"
        out.append({
            "provider": "Amadeus Flights",
            "providerCode": "amadeus",
            "price": float(price) if price else None,
            "carrier": carrier,
            "departure": dep,
            "arrival": arr,
            "raw": offer,
        })
    return out
